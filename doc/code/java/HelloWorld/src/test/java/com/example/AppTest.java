package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

/**
 * Unit tests for the App class.
 */
public class AppTest {

    /**
     * Test that the greet method returns the expected greeting.
     */
    @Test
    public void testGreet() {
        App app = new App();
        String result = app.greet("World");
        assertEquals("Hello, World!", result);
    }

    /**
     * Test that the greet method works with different names.
     */
    @Test
    public void testGreetWithDifferentName() {
        App app = new App();
        String result = app.greet("Java");
        assertEquals("Hello, Java!", result);
    }
}
