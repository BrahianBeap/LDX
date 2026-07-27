<?php

namespace Kanboard\Plugin\TeamWorkload;

use Kanboard\Core\Plugin\Base;
use Kanboard\Core\Translator;
use Kanboard\Core\Security\Role;

/**
 * TeamWorkload — vista de solo lectura: tareas abiertas de una persona
 * elegida, en todos los proyectos activos a los que pertenece.
 *
 * No modifica el Core. Reutiliza modelos ya existentes:
 * UserModel, ProjectUserRoleModel, ProjectGroupRoleModel, TaskFinderModel,
 * ColumnModel. Ver diseno-fase1.md en el repositorio de documentación
 * para el detalle completo de arquitectura y las decisiones tomadas.
 */
class Plugin extends Base
{
    public function initialize()
    {
        // Solo administradores durante la Fase 1 (ver diseno-fase1.md,
        // sección 4). El admin ya tiene visibilidad global por su rol —
        // el alcance de proyectos que consulta este plugin se calcula a
        // partir del usuario ELEGIDO, no del admin que consulta.
        $this->applicationAccessMap->add('WorkloadController', '*', Role::APP_ADMIN);

        $this->route->addRoute('workload', 'WorkloadController', 'show', 'TeamWorkload');

        $this->template->hook->attach('template:dashboard:sidebar', 'TeamWorkload:workload/sidebar');
    }

    public function onStartup()
    {
        Translator::load($this->languageModel->getCurrentLanguage(), __DIR__.'/Locale');
    }

    public function getPluginName()
    {
        return 'TeamWorkload';
    }

    public function getPluginDescription()
    {
        return t('Shows all open tasks of a chosen person across every project they belong to.');
    }

    public function getPluginAuthor()
    {
        return 'Equipo LDX';
    }

    public function getPluginVersion()
    {
        return '1.0.0';
    }
}
