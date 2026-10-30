<?php

namespace Kanboard\Plugin\OAuth2\Auth;

use Kanboard\Core\Base;
use Kanboard\Core\Security\OAuthAuthenticationProviderInterface;
use Kanboard\Plugin\OAuth2\User\SdiUserProvider;

/**
 * Proveedor de autenticación "SdiAd".
 *
 * Vincula la cuenta de AD con el usuario local por el correo: la parte
 * antes de la @ de "mail" (nombre.apellido@personal.com.py) tiene que ser
 * el username de Kanboard. No crea usuarios: sin coincidencia, rechaza.
 */
class SdiAuthProvider extends Base implements OAuthAuthenticationProviderInterface
{
    const DOMAIN = '@personal.com.py';

    protected $code = '';
    protected $user = null;
    protected $service = null;
    protected $error = '';

    public function getName()
    {
        return 'SdiAd';
    }

    public function authenticate()
    {
        $claims = $this->getService()->getClaims($this->code);

        if (empty($claims)) {
            $this->error = 'No se pudo validar el ingreso con AD. Probá de nuevo o ingresá con tu contraseña.';
            return false;
        }

        $tppy = isset($claims['sub']) && is_scalar($claims['sub']) ? (string) $claims['sub'] : '';
        $mail = isset($claims['mail']) && is_scalar($claims['mail']) ? strtolower(trim($claims['mail'])) : '';

        if (substr($mail, -strlen(self::DOMAIN)) !== self::DOMAIN) {
            $this->logger->info('SdiAd: '.$tppy.' sin correo '.self::DOMAIN.' en el token ('.$mail.')');
            $this->error = 'Tu cuenta de AD no tiene un correo '.self::DOMAIN.'. Ingresá con tu contraseña.';
            return false;
        }

        $username = substr($mail, 0, -strlen(self::DOMAIN));
        $profile = $this->userModel->getByUsername($username);

        if (empty($profile)) {
            $this->logger->info('SdiAd: '.$tppy.' ('.$mail.') no tiene usuario en Kanboard');
            $this->error = 'No hay un usuario "'.$username.'" en Kanboard. Pedí el alta a un administrador.';
            return false;
        }

        $this->logger->info('SdiAd: '.$tppy.' ingresó como '.$username);
        $this->user = new SdiUserProvider($profile);

        return true;
    }

    public function getUser()
    {
        return $this->user;
    }

    public function unlink($userId)
    {
        return false;
    }

    public function getService()
    {
        if ($this->service === null) {
            $this->service = new SdiOAuthService($this->container);
        }

        return $this->service;
    }

    public function setCode($code)
    {
        $this->code = $code;
        return $this;
    }

    public function getError()
    {
        return $this->error;
    }
}
