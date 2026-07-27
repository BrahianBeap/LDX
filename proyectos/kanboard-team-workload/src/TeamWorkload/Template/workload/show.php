<div class="page-header">
    <h2><?= $this->text->e($title) ?></h2>
</div>

<?= $this->app->component('select-dropdown-autocomplete', array(
    'name' => 'user_id',
    'items' => $all_users,
    'defaultValue' => $selected_user_id,
    'ariaLabel' => t('Choose a person'),
    'redirect' => array(
        'regex' => 'USER_ID',
        'url' => $this->url->to('WorkloadController', 'show', array('user_id' => 'USER_ID', 'plugin' => 'TeamWorkload')),
    ),
)) ?>

<br>

<?php if ($error !== ''): ?>

    <p class="alert alert-error"><?= $this->text->e($error) ?></p>

<?php elseif (! $everybody_mode && $selected_user === null): ?>

    <p class="alert"><?= t('Choose a person to see their workload.') ?></p>

<?php elseif (! $everybody_mode && empty($grouped_tasks)): ?>

    <p class="alert">
        <?= t('%s has no open tasks assigned in any active project.', $this->text->e($selected_user['name'] ?: $selected_user['username'])) ?>
    </p>

<?php else: ?>

    <?php if ($everybody_mode): ?>
        <table class="table-small">
            <tr>
                <td><strong><?= t('Users with tasks') ?>:</strong> <?= $summary['users_with_tasks'] ?></td>
                <td><strong><?= t('Projects') ?>:</strong> <?= $summary['projects'] ?></td>
                <td><strong><?= t('Open tasks') ?>:</strong> <?= $summary['open_tasks'] ?></td>
                <td><strong><?= t('Unassigned') ?>:</strong> <?= $summary['unassigned'] ?></td>
            </tr>
        </table>
        <br>
    <?php endif ?>

    <?php if (empty($grouped_tasks)): ?>

        <p class="alert"><?= t('There are no open tasks in any active project.') ?></p>

    <?php else: ?>

        <?php $total = 0; ?>
        <?php foreach ($grouped_tasks as $project_id => $group): ?>
            <?php $total += count($group['tasks']); ?>

            <h3><?= $this->url->link($this->text->e($group['name']), 'BoardViewController', 'show', array('project_id' => $project_id)) ?></h3>

            <table class="table-small table-striped table-scrolling">
                <tr>
                    <th class="column-5"><?= t('Id') ?></th>
                    <th class="column-15"><?= t('Column') ?></th>
                    <th><?= t('Title') ?></th>
                    <?php if ($everybody_mode): ?>
                        <th class="column-15"><?= t('Assignee') ?></th>
                    <?php endif ?>
                    <th class="column-10"><?= t('Priority') ?></th>
                    <th class="column-15"><?= t('Due date') ?></th>
                </tr>
                <?php foreach ($group['tasks'] as $task): ?>
                <tr>
                    <td class="task-table color-<?= $this->text->e($task['color_id']) ?>">
                        <?= $this->url->link('#'.$this->text->e($task['id']), 'TaskViewController', 'show', array('task_id' => $task['id']), false, '', t('View this task')) ?>
                    </td>
                    <td><?= $this->text->e($task['column_name']) ?></td>
                    <td>
                        <?= $this->url->link($this->text->e($task['title']), 'TaskViewController', 'show', array('task_id' => $task['id']), false, '', t('View this task')) ?>
                    </td>
                    <?php if ($everybody_mode): ?>
                        <td>
                            <?php if ($task['assignee_username']): ?>
                                <?= $this->text->e($task['assignee_name'] ?: $task['assignee_username']) ?>
                            <?php else: ?>
                                <?= t('Unassigned') ?>
                            <?php endif ?>
                        </td>
                    <?php endif ?>
                    <td><?= $this->text->e($task['priority']) ?></td>
                    <td>
                        <?php if ((int) $task['date_due'] > 0): ?>
                            <?= $this->dt->date($task['date_due']) ?>
                        <?php else: ?>
                            <?= t('No due date') ?>
                        <?php endif ?>
                    </td>
                </tr>
                <?php endforeach ?>
            </table>

        <?php endforeach ?>

        <p><?= t('Total: %d open tasks in %d projects', $total, count($grouped_tasks)) ?></p>

    <?php endif ?>

<?php endif ?>
