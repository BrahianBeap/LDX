<?php if ($this->user->isAdmin()): ?>
    <li <?= $this->app->checkMenuSelection('WorkloadController', 'show', 'TeamWorkload') ?>>
        <?= $this->url->link(t('Team workload'), 'WorkloadController', 'show', array('plugin' => 'TeamWorkload')) ?>
    </li>
<?php endif ?>
