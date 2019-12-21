<?php

function post_connect_add_user_id_as_base_dn() {
        $args = func_get_args();

        $user_dn = $args[2];

        if (substr($user_dn, 0, 12) === 'cn=admin,dc=') {
                return true;
        }

        $server = $_SESSION[APPCONFIG]->getServer($args[0]);

        $new_basedn = array($args[2]);
        $old_basedn = $server->getValue('server','base');

        if ($new_basedn != $old_basedn) {
                $server->setValue('server','base',array($user_dn));
        }

        return true;
}
add_hook('post_connect','post_connect_add_user_id_as_base_dn')

?>
