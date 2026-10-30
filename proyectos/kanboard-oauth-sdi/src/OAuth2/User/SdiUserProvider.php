<?php

namespace Kanboard\Plugin\OAuth2\User;

use Kanboard\Core\User\UserProviderInterface;

/**
 * Usuario local ya existente. Al devolver getInternalId(), el Core
 * (UserProfile::initialize) inicia la sesión con ese usuario sin
 * sincronizar ni crear nada.
 */
class SdiUserProvider implements UserProviderInterface
{
    protected $profile;

    public function __construct(array $profile)
    {
        $this->profile = $profile;
    }

    public function isUserCreationAllowed()
    {
        return false;
    }

    public function getExternalIdColumn()
    {
        return '';
    }

    public function getInternalId()
    {
        return $this->profile['id'];
    }

    public function getExternalId()
    {
        return '';
    }

    public function getRole()
    {
        return $this->profile['role'];
    }

    public function getUsername()
    {
        return $this->profile['username'];
    }

    public function getName()
    {
        return $this->profile['name'];
    }

    public function getEmail()
    {
        return $this->profile['email'];
    }

    public function getExternalGroupIds()
    {
        return array();
    }

    public function getExtraAttributes()
    {
        return array();
    }
}
