

requirejs.config {
    baseUrl: '/static/pwmanager/js/lib',

    paths: {
        app: '../app'
    }

    shim: {
        'reconnecting-websocket': {
            exports: 'ReconnectingWebSocket'
        },
        'knockout': {
            deps: ['jquery'],
            exports: 'ko'
        },
        'sammy': { deps: ['jquery'], exports: 'Sammy' },
    }

}

requirejs [
    'jquery',
    'sammy',
    'app/ui',
], ($, Sammy, PywizardUI) ->

    ui = new PywizardUI(global_data)
    ui.run()


