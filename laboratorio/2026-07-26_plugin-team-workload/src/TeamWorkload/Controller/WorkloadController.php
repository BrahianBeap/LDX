<?php

namespace Kanboard\Plugin\TeamWorkload\Controller;

use Kanboard\Controller\BaseController;
use Kanboard\Model\TaskModel;

/**
 * Única clase de lógica propia del plugin. Todo el acceso a datos se
 * apoya en modelos ya existentes del Core — ver diseno-fase1.md.
 */
class WorkloadController extends BaseController
{
    public function show()
    {
        $user_id = $this->request->getIntegerParam('user_id', 0);

        // Sin "prepend": esto excluye a propósito la opción "Everybody"
        // del selector (evita el defecto de ProjectUserOverviewController
        // de caer a "todos" cuando no hay un usuario real elegido) y ya
        // viene filtrado a usuarios activos y ordenado por nombre visible
        // (UserModel::prepareList() hace asort() sobre el nombre completo).
        $all_users = $this->userModel->getActiveUsersList();

        $params = array(
            'title' => t('Team workload'),
            'all_users' => $all_users,
            'selected_user_id' => $user_id,
            'selected_user' => null,
            'grouped_tasks' => array(),
            'error' => '',
        );

        if ($user_id > 0) {
            $user = $this->userModel->getById($user_id);

            if (empty($user)) {
                // A propósito NO cae a mostrar las tareas de todo el
                // mundo — ese es el defecto real confirmado en
                // ProjectUserOverviewController (ver informe de
                // investigación, sección 10.2).
                $params['error'] = t('User not found.');
            } else {
                $params['selected_user'] = $user;
                $params['grouped_tasks'] = $this->getGroupedOpenTasks($user_id);
            }
        }

        $this->response->html($this->helper->layout->app('TeamWorkload:workload/show', $params));
    }

    /**
     * Tareas abiertas del usuario ELEGIDO, agrupadas por proyecto.
     *
     * Importante (decisión explícita, ver diseno-fase1.md sección 1):
     * los proyectos se calculan a partir de las membresías reales del
     * usuario ELEGIDO (ProjectUserRoleModel + ProjectGroupRoleModel),
     * no del administrador que consulta. El admin ya tiene visibilidad
     * global por su rol (Role::APP_ADMIN, ver Plugin.php) — no
     * corresponde intersectar con sus propios proyectos.
     *
     * Si en el futuro se habilita el acceso a Role::APP_MANAGER, este
     * alcance debe revisarse explícitamente antes de reutilizar el mismo
     * criterio: un manager no-admin probablemente no deba poder consultar
     * a un usuario en proyectos a los que el propio manager no pertenece.
     *
     * @param  integer $user_id
     * @return array   [project_id => ['name' => string, 'tasks' => array]]
     */
    private function getGroupedOpenTasks($user_id)
    {
        $project_ids = array_unique(array_merge(
            array_keys($this->projectUserRoleModel->getActiveProjectsByUser($user_id)),
            array_keys($this->projectGroupRoleModel->getProjectsByUser($user_id))
        ));

        if (empty($project_ids)) {
            return array();
        }

        // Mismo método que usa el Core en
        // ProjectUserOverviewController::tasks() — ya trae project_name,
        // column_name, priority y color_id sin joins propios.
        $tasks = $this->taskFinderModel
            ->getProjectUserOverviewQuery($project_ids, TaskModel::STATUS_OPEN)
            ->eq(TaskModel::TABLE.'.owner_id', $user_id)
            ->findAll();

        if (empty($tasks)) {
            return array();
        }

        $grouped = array();

        foreach ($tasks as $task) {
            if (! isset($grouped[$task['project_id']])) {
                $grouped[$task['project_id']] = array(
                    'name' => $task['project_name'],
                    'tasks' => array(),
                );
            }

            $grouped[$task['project_id']]['tasks'][] = $task;
        }

        foreach ($grouped as $project_id => &$group) {
            $group['tasks'] = $this->sortTasksByColumnPriorityAndDueDate($project_id, $group['tasks']);
        }
        unset($group);

        // Proyectos en orden alfabético (criterio pedido explícitamente,
        // no viene resuelto por la consulta reutilizada).
        uasort($grouped, function ($a, $b) {
            return strcasecmp($a['name'], $b['name']);
        });

        return $grouped;
    }

    /**
     * Orden determinista dentro de cada proyecto: posición real de la
     * columna en el tablero (no el nombre) -> prioridad descendente ->
     * vencimiento ascendente, con las tareas sin fecha (date_due = 0)
     * al final.
     *
     * La consulta reutilizada no trae la posición de columna (solo el
     * nombre) — se resuelve con ColumnModel::getAll(), ya existente en
     * el Core y ya ordenado por posición, sin agregar SQL propio.
     *
     * @param  integer $project_id
     * @param  array   $tasks
     * @return array
     */
    private function sortTasksByColumnPriorityAndDueDate($project_id, array $tasks)
    {
        $positions = array();

        foreach ($this->columnModel->getAll($project_id) as $column) {
            $positions[$column['title']] = $column['position'];
        }

        usort($tasks, function ($a, $b) use ($positions) {
            $posA = isset($positions[$a['column_name']]) ? $positions[$a['column_name']] : PHP_INT_MAX;
            $posB = isset($positions[$b['column_name']]) ? $positions[$b['column_name']] : PHP_INT_MAX;

            if ($posA !== $posB) {
                return $posA <=> $posB;
            }

            if ($a['priority'] !== $b['priority']) {
                return $b['priority'] <=> $a['priority'];
            }

            $dueA = ((int) $a['date_due']) === 0 ? PHP_INT_MAX : (int) $a['date_due'];
            $dueB = ((int) $b['date_due']) === 0 ? PHP_INT_MAX : (int) $b['date_due'];

            return $dueA <=> $dueB;
        });

        return $tasks;
    }
}
