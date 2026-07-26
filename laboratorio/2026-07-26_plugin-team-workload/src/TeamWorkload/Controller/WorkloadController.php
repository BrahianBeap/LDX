<?php

namespace Kanboard\Plugin\TeamWorkload\Controller;

use Kanboard\Controller\BaseController;
use Kanboard\Model\ProjectModel;
use Kanboard\Model\TaskModel;
use Kanboard\Model\UserModel;

/**
 * Única clase de lógica propia del plugin. Todo el acceso a datos se
 * apoya en modelos ya existentes del Core — ver diseno-fase1.md y
 * diseno-v1.1.md.
 */
class WorkloadController extends BaseController
{
    public function show()
    {
        // No se usa getIntegerParam(): valida con ctype_digit(), que
        // rechaza el signo "-" y por lo tanto NUNCA deja pasar
        // UserModel::EVERYBODY_ID (-1) — confirmado leyendo
        // app/Core/Http/Request.php del Core. Se lee el valor crudo y se
        // castea con (int), que sí interpreta "-1" correctamente.
        $user_id = (int) $this->request->getStringParam('user_id', '0');

        // UserModel::EVERYBODY_ID (-1) es la misma constante que ya usa
        // el Core en ProjectUserOverviewController para el modo "todos".
        // Se prepende a mano (en vez de getActiveUsersList(true)) para no
        // reutilizar la traducción compartida 'Everybody' del Core, que
        // cambiaría también el texto de otras pantallas del propio
        // Kanboard si se la sobreescribe (ver diseno-v1.1.md, sección 1).
        $all_users = array(UserModel::EVERYBODY_ID => t('👥 All')) + $this->userModel->getActiveUsersList();

        $params = array(
            'title' => t('Team workload'),
            'all_users' => $all_users,
            'selected_user_id' => $user_id,
            'selected_user' => null,
            'everybody_mode' => false,
            'grouped_tasks' => array(),
            'summary' => null,
            'error' => '',
        );

        if ($user_id === UserModel::EVERYBODY_ID) {
            $params['everybody_mode'] = true;
            $tasks = $this->getOpenTasks(UserModel::EVERYBODY_ID, $this->getAllActiveProjectIds());
            $params['grouped_tasks'] = $this->groupByProject($tasks);
            $params['summary'] = $this->buildSummary($tasks, $params['grouped_tasks']);
        } elseif ($user_id > 0) {
            $user = $this->userModel->getById($user_id);

            if (empty($user)) {
                // A propósito NO cae a mostrar las tareas de todo el
                // mundo — ese es el defecto real confirmado en
                // ProjectUserOverviewController (ver informe de
                // investigación, sección 10.2).
                $params['error'] = t('User not found.');
            } else {
                $params['selected_user'] = $user;
                $project_ids = $this->getProjectIdsForUser($user_id);
                $tasks = $this->getOpenTasks($user_id, $project_ids);
                $params['grouped_tasks'] = $this->groupByProject($tasks);
            }
        }

        $this->response->html($this->helper->layout->app('TeamWorkload:workload/show', $params));
    }

    /**
     * Proyectos ACTIVOS del usuario ELEGIDO (decisión explícita, ver
     * diseno-fase1.md sección 1): nunca intersectados con los del
     * administrador que consulta — el admin ya tiene visibilidad global
     * por su rol (Role::APP_ADMIN, ver Plugin.php).
     *
     * @param  integer $user_id
     * @return array
     */
    private function getProjectIdsForUser($user_id)
    {
        return array_unique(array_merge(
            array_keys($this->projectUserRoleModel->getActiveProjectsByUser($user_id)),
            array_keys($this->projectGroupRoleModel->getProjectsByUser($user_id))
        ));
    }

    /**
     * IDs de todos los proyectos ACTIVOS del sistema, para el modo
     * "todos" (el admin ya tiene visibilidad global por su rol).
     *
     * `ProjectModel::getAllIds()` (usado por el propio Core en
     * `ProjectUserOverviewController::common()` para el mismo caso)
     * incluye proyectos inactivos/archivados — no es lo que se necesita
     * acá, porque el modo individual sí los excluye
     * (`getActiveProjectsByUser()`). Se usa en cambio
     * `getAllByStatus(ProjectModel::ACTIVE)`, también ya existente en el
     * Core, para mantener el mismo criterio en ambos modos.
     *
     * @return array
     */
    private function getAllActiveProjectIds()
    {
        return array_column($this->projectModel->getAllByStatus(ProjectModel::ACTIVE), 'id');
    }

    /**
     * Tareas abiertas en los proyectos indicados.
     *
     * Reutiliza tal cual `TaskFinderModel::getProjectUserOverviewQuery()`
     * — el mismo método que usa el Core en
     * `ProjectUserOverviewController::tasks()` — que YA no filtra por
     * propietario. Ese filtro lo agrega el propio Core (y antes, este
     * plugin) encadenando `.eq('owner_id', $user_id)` por fuera; para el
     * modo "todos" (`UserModel::EVERYBODY_ID`) simplemente no se agrega
     * esa condición. No hizo falta ninguna consulta nueva para esto — ver
     * diseno-v1.1.md, sección "Análisis previo".
     *
     * `getProjectUserOverviewQuery()` ya incluye `assignee_username` y
     * `assignee_name` en cada fila (confirmado leyendo el código real del
     * Core), así que tampoco hizo falta ningún join propio para mostrar
     * el responsable de cada tarea en el modo "todos".
     *
     * @param  integer $user_id      UserModel::EVERYBODY_ID para el modo "todos"
     * @param  array   $project_ids
     * @return array
     */
    private function getOpenTasks($user_id, array $project_ids)
    {
        if (empty($project_ids)) {
            return array();
        }

        $query = $this->taskFinderModel->getProjectUserOverviewQuery($project_ids, TaskModel::STATUS_OPEN);

        if ($user_id !== UserModel::EVERYBODY_ID) {
            $query->eq(TaskModel::TABLE.'.owner_id', $user_id);
        }

        return $query->findAll();
    }

    /**
     * Agrupa una lista de tareas por proyecto, ordenando cada grupo y los
     * proyectos entre sí.
     *
     * Punto de extensión para futuros modos de agrupación (ver
     * diseno-v1.1.md, sección "Camino para futuras vistas"): esta es la
     * única estrategia de agrupación implementada hoy (por proyecto). Un
     * agrupamiento nuevo (por persona, por prioridad, por vencimiento)
     * se agregaría como un método hermano — por ejemplo
     * `groupByAssignee(array $tasks)` — que recorre la misma lista de
     * tareas ya obtenida por `getOpenTasks()`, sin tocar la consulta ni
     * el resto del controlador.
     *
     * @param  array $tasks
     * @return array [project_id => ['name' => string, 'tasks' => array]]
     */
    private function groupByProject(array $tasks)
    {
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

    /**
     * Resumen del modo "todos" — calculado en PHP puro sobre la lista de
     * tareas ya obtenida, sin ninguna consulta adicional.
     *
     * Nota: `getProjectUserOverviewQuery()` no incluye `owner_id` en las
     * columnas devueltas (solo `assignee_username`/`assignee_name`, ya
     * resueltos vía el LEFT JOIN que el propio Core arma contra
     * `owner_id`) — se usa `assignee_username` como identificador único
     * de persona para esta cuenta, no `owner_id`.
     *
     * @param  array $tasks
     * @param  array $grouped_tasks
     * @return array
     */
    private function buildSummary(array $tasks, array $grouped_tasks)
    {
        $owners = array();
        $unassigned = 0;

        foreach ($tasks as $task) {
            if (empty($task['assignee_username'])) {
                $unassigned++;
            } else {
                $owners[$task['assignee_username']] = true;
            }
        }

        return array(
            'users_with_tasks' => count($owners),
            'projects' => count($grouped_tasks),
            'open_tasks' => count($tasks),
            'unassigned' => $unassigned,
        );
    }
}
