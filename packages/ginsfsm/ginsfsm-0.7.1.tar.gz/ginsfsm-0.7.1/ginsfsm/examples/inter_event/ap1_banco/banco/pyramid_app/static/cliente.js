/*******************************************************************
 *  cliente.js
 *******************************************************************/

/**************************************************************************
 *        Cliente
 **************************************************************************/
;(function (exports) {
    'use strict';

    /************************************************************
     *      Cliente class.
     ************************************************************/
    /********************************************
     *      Default config
     *
     ********************************************/
    var CLIENTE_CONFIG = {
        // Id of dom element parent. It has preference over parent gobj.
        parent_dom_id: ''
    };

    /********************************************
     *      Auxiliary
     ********************************************/
    function IsNumeric(num) {
        return (num >=0 || num < 0);
    }

    function pon_texto(self, texto, $element) {
        $element.val(texto).select();
    }

    function init_controles(self) {
        pon_texto(self, "Regístrese!", self.$registro_button);
        self.$registro_nombre.prop('disabled', false);
        self.$registro_button.prop('disabled', false);
        self.$prestamo_button.prop('disabled', true);
        self.$acciones_button.prop('disabled', true);
        self.$prestamo_cantidad.prop('disabled', true);
        self.$acciones_cantidad.prop('disabled', true);

        pon_texto(self, "", self.$registro_resultado);
        pon_texto(self, "", self.$prestamo_cantidad);
        pon_texto(self, "", self.$acciones_cantidad);
        pon_texto(self, "", self.$prestamo_total);
        pon_texto(self, "", self.$acciones_total);
        pon_texto(self, "", self.$regalo_resultado);

        pon_texto(self, "Escriba su nombre", self.$registro_nombre);
    }

    /********************************************
     *      Configure events
     ********************************************/
    function configure_item_events(self) {
        /*--------------------------------*
         *      Set DOM events
         *--------------------------------*/

        /*
         *  Get our DOM elements
         */
        self.$registro_nombre = $('#registro_nombre');
        self.$registro_button = $('#registro_button');
        self.$registro_resultado = $('#registro_resultado');

        self.$prestamo_cantidad = $('#prestamo_cantidad');
        self.$prestamo_button = $('#prestamo_button');
        self.$prestamo_total = $('#prestamo_total');

        self.$acciones_cantidad = $('#acciones_cantidad');
        self.$acciones_button = $('#acciones_button');
        self.$acciones_total = $('#acciones_total');

        self.$regalo_button = $('#regalo_button');
        self.$regalo_resultado = $('#regalo_resultado');

        /*
         *  Configure events
         */
        self.$registro_button.on("click", self, function(event){
            event.stopPropagation();
            var self = event.data;
            var kw = {
                user_name: self.$registro_nombre.val()
            };
            self.send_event(self, 'EV_REGISTER_USER', kw);
        });

        self.$prestamo_button.on("click", self, function(event){
            event.stopPropagation();
            var self = event.data;
            var kw = {
                euros: self.$prestamo_cantidad.val()
            };
            self.send_event(self, 'EV_PEDIR_PRESTAMO', kw);
        });

        self.$acciones_button.on("click", self, function(event){
            event.stopPropagation();
            var self = event.data;
            var kw = {
                acciones: self.$acciones_cantidad.val()
            };
            self.send_event(self, 'EV_COMPRAR_ACCIONES', kw);
        });

        self.$regalo_button.on("click", self, function(event){
            event.stopPropagation();
            var self = event.data;
            var kw = {
            };
            self.send_event(self, 'EV_SUBSCRIBE_REGALO', kw);
        });

        return 1;
    }

    /***************************************************************
     *      Actions
     ***************************************************************/
    function ac_register_user(self, event) {
        /*
         *  user_name =
         */
        var user_name = event.kw.user_name;
        if (!user_name || user_name == "Escriba su nombre") {
            pon_texto(self, "Escriba su nombre", self.$registro_nombre);
            return 1;
        }
        pon_texto(self, "Espere por favor...", self.$registro_resultado);
        self.user_name = user_name;

        self.gaplic.send_event_outside(
            '',                 // gaplic
            'banco',            // role
            'cuentas',          // gobj_name
            'EV_CUENTA',        // event_name
            self,               // subscriber_gobj
            null,               // origin_role
            {                   // kw
                user_name: user_name
            }
        );

        return 1;
    }

    function ac_unregister_user(self, event) {
        init_controles(self);
        return 1;
    }

    function ac_cuenta_ack(self, event) {
        pon_texto(self, "Deregistrarse", self.$registro_button);
        pon_texto(self, "Registrado!", self.$registro_resultado);

        self.$registro_nombre.prop('disabled', true);
        self.$prestamo_button.prop('disabled', false);
        self.$acciones_button.prop('disabled', false);
        self.$prestamo_cantidad.prop('disabled', false);
        self.$acciones_cantidad.prop('disabled', false);

        pon_texto(self, "", self.$prestamo_cantidad);

        return 1;
    }

    function ac_pedir_prestamo(self, event) {
        var euros = event.kw.euros;

        if (!IsNumeric(euros) || euros <= 0) {
            pon_texto(self, "Escriba una cantidad", self.$prestamo_cantidad);
            return 1;
        }

        pon_texto(self, "Espere por favor...", self.$prestamo_total);

        self.gaplic.send_event_outside(
            '',                 // gaplic
            'financiera',       // role
            'prestamos',        // gobj_name
            'EV_PRESTAMO',      // event_name
            self,               // subscriber_gobj
            null,               // origin_role
            {                   // kw
                euros: euros,
                user_name: self.user_name
            }
        );

        return 1;
    }

    function ac_prestamo_ack(self, event) {
        var euros = event.kw.euros;

        pon_texto(self, euros, self.$prestamo_total);

        return 1;
    }

    function ac_comprar_acciones(self, event) {
        var acciones = event.kw.acciones;

        if (!IsNumeric(acciones)) {
            pon_texto(self, "Escriba una cantidad", self.$acciones_cantidad);
            return 1;
        }

        pon_texto(self, "Espere por favor...", self.$acciones_total);

        self.gaplic.send_event_outside(
            '',                 // gaplic
            'bolsa',            // role
            'acciones',         // gobj_name
            'EV_ACCIONES',      // event_name
            self,               // subscriber_gobj
            null,               // origin_role
            {                   // kw
                acciones: acciones,
                user_name: self.user_name
            }
        );

        return 1;
    }

    function ac_acciones_ack(self, event) {
        var acciones = event.kw.acciones;

        pon_texto(self, acciones, self.$acciones_total);

        return 1;
    }

    function ac_subscribe_regalo(self, event) {
        pon_texto(self, "Espere por favor...", self.$regalo_resultado);

        //self.gaplic.send_event_outside(
        //    '',                 // gaplic
        //    'publicidad',       // role
        //    'sorteo',           // gobj_name
        //    'EV_REGALO',        // event_name
        //    self,               // subscriber_gobj
        //    null,               // origin_role
        //    {                   // kw
        //        user_name: self.user_name
        //    }
        //);

        self.gaplic.subscribe_event_outside(
            '',             // gaplic_name
            'publicidad',   // role
            'sorteo',       // gobj_name
            'EV_REGALO',    // event_name
            self,           // subscriber_gobj
            null,           // origin_role
            {               // kw
                user_name: self.user_name
            }
        );
        return 1;
    }

    function ac_regalo(self, event) {
        var regalo = event.kw.regalo;

        pon_texto(self, regalo, self.$regalo_resultado);

        return 1;
    }

    /********************************************
     *      Automata
     ********************************************/
    var CLIENTE_FSM = {
        'event_list': [
            'EV_CUENTA_ACK',
            'EV_PRESTAMO_ACK',
            'EV_ACCIONES_ACK',
            'EV_PEDIR_PRESTAMO',
            'EV_COMPRAR_ACCIONES',
            'EV_SUBSCRIBE_REGALO',
            'EV_REGALO',
            'EV_REGISTER_USER'
        ],
        'state_list': [
            'ST_INIT',                       /* Estado inicial */
            'ST_REGISTERED',                 /* Usuario registrado */
            ],
        'machine': {
            'ST_INIT':
            [
                ['EV_CUENTA_ACK',       ac_cuenta_ack,       'ST_REGISTERED'],
                ['EV_REGISTER_USER',    ac_register_user,    undefined]
            ],
            'ST_REGISTERED':
            [
                ['EV_REGISTER_USER',    ac_unregister_user,  'ST_INIT'],
                ['EV_PEDIR_PRESTAMO',   ac_pedir_prestamo,   undefined],
                ['EV_COMPRAR_ACCIONES', ac_comprar_acciones, undefined],
                ['EV_SUBSCRIBE_REGALO', ac_subscribe_regalo, undefined],
                ['EV_REGALO',           ac_regalo,           undefined],
                ['EV_PRESTAMO_ACK',     ac_prestamo_ack,     undefined],
                ['EV_ACCIONES_ACK',     ac_acciones_ack,     undefined]
            ]
        }
    }

    /********************************************
     *      Class
     ********************************************/
    var Cliente = GObj.__makeSubclass__();
    var proto = Cliente.prototype; // Easy access to the prototype
    proto.__init__= function(name, parent, kw, gaplic) {
        this.name = name || '';  // set before super(), to put the same smachine name
        GObj.prototype.__init__.call(this, CLIENTE_FSM, CLIENTE_CONFIG);
        __update_dict__(this.config, kw || {});
        return this;
    };
    proto.start_up= function() {
        //**********************************
        //  start_up
        //**********************************
        var self = this;
        configure_item_events(self);

        /*-------------------------------------------------*
         *  Initial paint
         *  Paint will set $head and $tail insert point.
         *-------------------------------------------------*/
        //self.send_event(self, 'EV_REGISTER_USER');

        /*---------------------------------*
         *      Build jquery link list.
         *---------------------------------*/
        self.build_jquery_link_list();

        init_controles(self);
    }

    /*--------------------------------------*
     *      High level functions
     *--------------------------------------*/
    /*--------------------------*
     *
     *--------------------------*/
    proto.setCheck = function (checked) {
        var self = this;
        /*
        if (checked) {
            var cur_st = self.get_current_state();
            if (cur_st !== 'ST_PRESSED') {
                self.set_new_state('ST_PRESSED');
                self.send_event(self, 'EV_REGISTER_USER');
            }
        } else {
            var cur_st = self.get_current_state();
            if (cur_st !== 'ST_NORMAL') {
                self.set_new_state('ST_NORMAL');
                self.send_event(self, 'EV_REGISTER_USER');
            }
        }
        */
    }

    /*--------------------------*
     *
     *--------------------------*/
    proto.setEnable = function (enabled) {
        /*
        var self = this;
        if (enabled) {
            self.set_new_state('ST_NORMAL');
            self.send_event(self, 'EV_REGISTER_USER');
        } else {
            self.set_new_state('ST_DISABLED');
            self.send_event(self, 'EV_REGISTER_USER');
        }
        */
    }
    exports.Cliente = Cliente;
}(this));
