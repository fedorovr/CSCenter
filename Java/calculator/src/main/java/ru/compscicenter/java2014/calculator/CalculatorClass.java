package ru.compscicenter.java2014.calculator;

/**
 * Created by Roman Fedorov on 15.10.2014.
 */

public class CalculatorClass implements Calculator{

    private enum Operator {
        ADDITION('+') {
            @Override
            public double apply(double leftOperand, double rightOperand) {
                return leftOperand + rightOperand;
            }
        },
        SUBTRACTION('-') {
            @Override
            public double apply(double leftOperand, double rightOperand) {
                return leftOperand - rightOperand;
            }
        },
        MULTIPLICATION('*') {
            @Override
            public double apply(double leftOperand, double rightOperand) { return leftOperand * rightOperand; }
        },
        DIVISION('/') {
            @Override
            public double apply(double leftOperand, double rightOperand) {
                return leftOperand / rightOperand;
            }
        },
        EXPONENTATION('^') {
            @Override
            public double apply(double leftOperand, double rightOperand) {
                return Math.pow(leftOperand, rightOperand);
            }
        },
        SINE('s') {
            @Override
            public double apply(double leftOperand, double rightOperand) {
                return Math.sin(rightOperand);
            }
        },
        COSINE('c') {
            @Override
            public double apply(double leftOperand, double rightOperand) {
                return Math.cos(rightOperand);
            }
        },
        ABSOLUTE_VALUE('a') {
            @Override
            public double apply(double leftOperand, double rightOperand) { return Math.abs(rightOperand); }
        },
        SCIENTIFIC_FORM('e'){
            @Override
            public double apply(double leftOperand, double rightOperand) { return 0.0; }
        };

        private final char code;

        private Operator(char code) {
            this.code = code;
        }

        public static Operator buildOperator(char code) {
            for (Operator operator: Operator.values()) {
                if (code == operator.code) {
                    return operator;
                }
            }
            return null;
        }

        public boolean isOperatorEquals(Operator... operators) {
            for (Operator operator: operators) {
                if (this.equals(operator)) {
                    return true;
                }
            }
            return false;
        }

        public abstract double apply(double leftOperand, double rightOperand);
    }

    private double parseFactor(String currentExpression) {
        currentExpression = CustomStringUtils.deleteBrackets(currentExpression);
        try {
            return Double.parseDouble(currentExpression);
        }
        catch (NumberFormatException e) {
            return parseExpression(currentExpression);
        }
    }

    private double parseFunction(String currentExpression) {
        CustomStringUtils tmpString = new CustomStringUtils(currentExpression);
        tmpString.deleteBrackets(currentExpression);
        currentExpression = tmpString.getString();
        Operator operatorOne = Operator.buildOperator(currentExpression.charAt(0));
        if((operatorOne != null) && (operatorOne.isOperatorEquals(Operator.ABSOLUTE_VALUE, Operator.SINE, Operator.COSINE))){
            return operatorOne.apply(0.0, parseExpression(currentExpression.substring(3, currentExpression.length())));
        }
        else {                                          //no function
            return parseFactor(currentExpression);
        }
    }

    private double parseDegree(String currentExpression) {
        CustomStringUtils tmpString = new CustomStringUtils(currentExpression);
        tmpString.deleteBrackets(currentExpression);
        currentExpression = tmpString.getString();
        char[] currentCharArray = currentExpression.toCharArray();
        for (int charPosition = 0; charPosition < currentExpression.length(); charPosition++) {
            if (currentCharArray[charPosition] == '(') {
                charPosition = tmpString.findClosingBracketToRight(charPosition + 1, currentExpression.length(), currentCharArray);
            }
            else{
                if (currentCharArray[charPosition] == '^')  {
                    Operator operatorOne = Operator.buildOperator(currentCharArray[charPosition]);
                    return operatorOne.apply(parseExpression(currentExpression.substring(0, charPosition)), parseExpression(currentExpression.substring(charPosition + 1, currentExpression.length())));
                }
            }
        }
        return parseFunction(currentExpression);        //no ^
    }

    private double parseProduct(String currentExpression) {
        CustomStringUtils tmpString = new CustomStringUtils(currentExpression);
        tmpString.deleteBrackets(currentExpression);
        currentExpression = tmpString.getString();
        char[] currentCharArray = currentExpression.toCharArray();
        for (int charPosition = currentExpression.length() - 1; charPosition >= 0; charPosition--) {
            if (currentCharArray[charPosition] == ')') {
                charPosition = tmpString.findClosingBracketToLeft(charPosition - 1, currentCharArray);
            } else {
                if ((currentCharArray[charPosition] == '*') || (currentCharArray[charPosition] == '/')) {
                    Operator operatorOne = Operator.buildOperator(currentCharArray[charPosition]);
                    return operatorOne.apply(parseExpression(currentExpression.substring(0, charPosition)), parseExpression(currentExpression.substring(charPosition + 1, currentExpression.length())));
                }
            }
        }
        return parseDegree(currentExpression);          //no * or /
    }

    private double parseExpression(String currentExpression) {
        CustomStringUtils tmpString = new CustomStringUtils(currentExpression);
        tmpString.deleteBrackets(currentExpression);
        currentExpression = tmpString.getString();
        if((currentExpression.charAt(0) == '-') || (currentExpression.charAt(0) == '+')) {
            currentExpression = '0' + currentExpression;
        }
        char[] currentCharArray = currentExpression.toCharArray();
        for(int charPosition = currentExpression.length() - 1; charPosition >= 0; charPosition--) {
            if (currentCharArray[charPosition] == ')') {
                charPosition = tmpString.findClosingBracketToLeft(charPosition - 1, currentCharArray);
            }
            else {
                if ((currentCharArray[charPosition] == '+') || (currentCharArray[charPosition] == '-')) {
                    Operator operatorOne = Operator.buildOperator(currentCharArray[charPosition]);
                    if (Operator.buildOperator(currentCharArray[charPosition - 1]) == null) {
                        return operatorOne.apply(parseExpression(currentExpression.substring(0, charPosition)), parseExpression(currentExpression.substring(charPosition + 1, currentExpression.length())));
                    }
                }
            }
        }
        return parseProduct(currentExpression);
    }

    public double calculate(String expression) {
        expression = expression.toLowerCase();
        expression = expression.replaceAll("\\s", "");                            // removes spaces
        return parseExpression(expression);
    }
}