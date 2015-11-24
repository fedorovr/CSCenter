package ru.compscicenter.java2014.implementor.test;

import org.testng.annotations.Factory;

import java.util.Locale;
import java.util.Properties;

public class ImplementorTestFactory {

    @Factory
    public static Object[] createTests() throws Exception {
        Properties prop = new Properties();
        prop.load(ImplementorTestFactory.class.getClassLoader().getResourceAsStream("build.properties"));
        Locale.setDefault(Locale.US);
        return new Object[] { new ImplementorTest(Class.forName(prop.getProperty("IMPLEMENTATION_CLASS"))) };
    }

}
