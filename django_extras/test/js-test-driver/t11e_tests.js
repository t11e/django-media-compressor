TestCase("t11e", {
    testT11e: function() {
        assertEquals('object', typeof t11e);
    },

    testT11eEvent: function() {
        assertEquals('object', typeof t11e.event);
    },

    testT11e2: function() {
        assertEquals('undefined', typeof t11ee);
    },

    testSubscribe: function() {
        assertEquals('function', typeof t11e.event.subscribe);
        var counter = 0;
        var inc_counter = function() {
            counter += 1;
        };
        t11e.event.subscribe('count', inc_counter);
        assertEquals(0, counter);
        t11e.event.trigger('count', this);
        assertEquals(1, counter);

        var recorded_args = [];
        var arg_recorder = function() {
            recorded_args = Array.prototype.slice.call(arguments, 0);
        };

        arg_recorder(1, 2, 3);
        assertEquals([1, 2, 3], recorded_args);
        recorded_args = [];

        arg_recorder.apply(null, [1, 2, 3]);
        assertEquals([1, 2, 3], recorded_args);
        recorded_args = [];

        t11e.event.subscribe('record', arg_recorder);
        t11e.event.trigger('record', 1, 2, 3);
        assertEquals([1, 2, 3], recorded_args);
        assertEquals(1, counter);
    },

    testUnsubscribe: function() {
        assertEquals('function', typeof t11e.event.subscribe);
        assertEquals('function', typeof t11e.event.unsubscribe);
        var counter = 0;
        var inc_counter = function() {
            counter += 1;
        };

        t11e.event.trigger('count', this);
        assertEquals(0, counter);

        t11e.event.unsubscribe('count', inc_counter);
        t11e.event.trigger('count', this);
        assertEquals(0, counter);

        t11e.event.subscribe('count', inc_counter);
        t11e.event.trigger('count', this);
        assertEquals(1, counter);

        t11e.event.unsubscribe('count', inc_counter);
        t11e.event.trigger('count', this);
        assertEquals(1, counter);

        t11e.event.subscribe('count', inc_counter);
        t11e.event.trigger('count', this);
        assertEquals(2, counter);

        t11e.event.subscribe('count', inc_counter);
        t11e.event.trigger('count', this);
        assertEquals(3, counter);

        t11e.event.unsubscribe('count', inc_counter);
        t11e.event.trigger('count', this);
        assertEquals(3, counter);
    },

    testMultipleDifferentSubscribers: function() {
        var counter1 = 0;
        var inc_counter1 = function() {
            counter1 += 1;
        };
        var counter2 = 0;
        var inc_counter2 = function() {
            counter2 += 1;
        };

        t11e.event.subscribe('channel1', inc_counter1);
        t11e.event.subscribe('channel2', inc_counter2);
        assertEquals(0, counter1);
        assertEquals(0, counter2);

        t11e.event.trigger('channel1', this);
        assertEquals(1, counter1);
        assertEquals(0, counter2);

        t11e.event.trigger('channel2', this);
        assertEquals(1, counter1);
        assertEquals(1, counter2);

        t11e.event.subscribe('channel1', inc_counter2);
        t11e.event.trigger('channel1', this);
        assertEquals(2, counter1);
        assertEquals(2, counter2);

        t11e.event.trigger('channel2', this);
        assertEquals(2, counter1);
        assertEquals(3, counter2);
    },

    testMultipleSameSubscribers: function() {
        var counter = 0;
        var inc_counter = function() {
            counter += 1;
        };

        t11e.event.subscribe('channel1', inc_counter);
        t11e.event.subscribe('channel2', inc_counter);
        assertEquals(0, counter);

        t11e.event.trigger('channel1', this);
        assertEquals(1, counter);

        t11e.event.trigger('channel2', this);
        assertEquals(2, counter);

        t11e.event.subscribe('channel1', inc_counter);
        t11e.event.trigger('channel1', this);
        assertEquals(3, counter);

        t11e.event.trigger('channel2', this);
        assertEquals(4, counter);
    },

    testHandlerException: function() {
        var counter = 0;
        var inc_counter1 = function() {
            counter += 1;
        };
        var inc_counter2 = function() {
            counter += 1;
        };
        var thrower = function() {
            throw new Error("Test Exception");
        };
        // Temporarily disable console.log to make the tests more quiet.
        var old_console_log = console.log;
        console.log = function() {};
        try
        {
            t11e.event.subscribe('exception', inc_counter1);
            assertEquals(0, counter);

            t11e.event.trigger('exception', this);
            assertEquals(1, counter);

            t11e.event.subscribe('exception', thrower);
            t11e.event.trigger('exception', this);
            assertEquals(2, counter);

            t11e.event.subscribe('exception', inc_counter2);
            t11e.event.trigger('exception', this);
            assertEquals(4, counter);
        } finally {
            console.log = old_console_log;
        }
    }
});
