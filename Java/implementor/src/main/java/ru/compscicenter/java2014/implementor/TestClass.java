package ru.compscicenter.java2014.implementor;

/**
 * Created by Roman Fedorov on 30.11.2014.
 */
public class TestClass {
    public static void main(String[] args) {
        Implementor testImplementor = new ImplementorRealization("C:\\Documents\\tmpImpl\\output\\");
        try {
            testImplementor.implementFromDirectory("C:\\Documents\\tmpImpl", "ru.compscicenter.java2014.collections.MultiSet");
        }
        catch (ImplementorException ie) {

        }
    }
}
