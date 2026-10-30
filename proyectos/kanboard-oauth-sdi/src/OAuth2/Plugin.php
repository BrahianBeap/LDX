<?php

namespace Kanboard\Plugin\OAuth2;

use Kanboard\Core\Plugin\Base;
use Kanboard\Core\Security\Role;
use Kanboard\Plugin\OAuth2\Auth\SdiAuthProvider;

/**
 * Ingreso a Kanboard con la cuenta de AD, por el OAuth de SDI
 * (ciberseg.personal.com.py).
 *
 * La carpeta se llama OAuth2 porque la URL de retorno registrada en SDI
 * (623 #1085317) es ?controller=OAuthController&action=handler&plugin=OAuth2.
 * No es el plugin oficial "OAuth2" de Kanboard: SDI no sigue el estándar
 * (ver docs/00_Arquitectura.md).
 *
 * No modifica el Core ni crea usuarios: solo vincula la cuenta de AD con un
 * usuario local existente. El login con contraseña sigue funcionando.
 * Sin SDI_OAUTH_CLIENT_ID / SDI_OAUTH_CLIENT_SECRET en config.php, no hace nada.
 */
class Plugin extends Base
{
    public function initialize()
    {
        if (! defined('SDI_OAUTH_CLIENT_ID') || ! defined('SDI_OAUTH_CLIENT_SECRET')) {
            return;
        }

        $this->fixSdiCallbackUrl();

        $this->authenticationManager->register(new SdiAuthProvider($this->container));

        // El retorno de SDI llega sin sesión iniciada.
        $this->applicationAccessMap->add('OAuthController', 'handler', Role::APP_PUBLIC);

        $this->template->hook->attach('template:auth:login-form:after', 'OAuth2:auth/login');
    }

    /**
     * SDI agrega "?code=..." a la URL registrada aunque ya tenga "?", y el
     * retorno llega como plugin=OAuth2?code=XXX. El Router descarta ese
     * nombre de plugin ("Action not implemented"). Los plugins se cargan
     * antes de Router::dispatch(), así que se corrige acá.
     */
    protected function fixSdiCallbackUrl()
    {
        $plugin = $this->request->getStringParam('plugin');

        if (strpos($plugin, 'OAuth2?') !== 0) {
            return;
        }

        parse_str(substr($plugin, strlen('OAuth2?')), $params);
        $params['plugin'] = 'OAuth2';
        $this->request->setParams($params);
    }

    public function getPluginName()
    {
        return 'OAuth2';
    }

    public function getPluginDescription()
    {
        return 'Ingreso con la cuenta de AD por el OAuth de SDI (ciberseg.personal.com.py).';
    }

    public function getPluginAuthor()
    {
        return 'Equipo LDX';
    }

    public function getPluginVersion()
    {
        return '1.0.0';
    }

    public function getCompatibleVersion()
    {
        return '>=1.2.46';
    }
}
