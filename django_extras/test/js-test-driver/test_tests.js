TestCase("test", {
    testAssertEqualsNumber: function() {
        assertEquals(0, 1 - 1);
        assertEquals(2, 1 + 1);
        assertEquals(4, 2 + 2);
        assertNotEquals(3, 1 + 1);
    },

    testAssertEqualsString: function() {
        assertEquals("", "");
        assertEquals("abc", "ab" + "c");
        assertNotEquals("", "abc");
        assertNotEquals("aBc", "ab" + "c");
    },

    testAssertEqualsArray: function() {
        assertEquals([], []);
        assertEquals([1,2], [1,2]);
        assertNotEquals([], [1,2]);
        assertNotEquals([1,2], [3,4]);
    },

    testAssertEqualsObject: function() {
        assertEquals({}, {});
        assertEquals({'a': 'A'}, {'a': 'A'});
        assertNotEquals({}, {'A': 'a'});
        assertNotEquals({'a': 'A'}, {'A': 'a'});
    },

    testArgPassing: function() {
        var changer = function(kwargs) {
            kwargs.foo = 'bar';
        };
        var data = {};
        changer(data);
        assertEquals('bar', data.foo);

        data = {};
        changer.apply(null, [data]);
        assertEquals('bar', data.foo);
    }

});
