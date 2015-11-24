package ru.compscicenter.java2014.calculator;

public class testClass {

    public static void main(String[] args) {
        CalculatorClass a = new CalculatorClass();
        System.out.println(a.calculate("2+2e-2"));
        System.out.println(a.calculate("cos(0)"));
        System.out.println(a.calculate("2*-2"));
        System.out.println(a.calculate("2^3^4"));
        System.out.println(a.calculate("2-----------2"));
    }
}
