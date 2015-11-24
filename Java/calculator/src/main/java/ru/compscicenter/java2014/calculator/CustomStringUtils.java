package ru.compscicenter.java2014.calculator;

/**
 * Created by Roman Fedorov on 05.10.2014.
 */

public class CustomStringUtils {

    private String expressionString;

    public CustomStringUtils(String expressionString) {
        this.expressionString = expressionString;
    }

    public String getString() {
        return expressionString;
    }

    public static boolean checkBrackets(String str) {
        int len = str.length(), c = 0;
        char[] tempCharArray = str.toCharArray();
        for (int i = 0; i < len; i++) {
            if ((tempCharArray[i]) == '('){
                c++;
            }
            if ((tempCharArray[i]) == ')'){
                c--;
            }
            if (c < 0){
                return false;
            }
        }
        return (c == 0);
    }

    public static int findClosingBracketToRight(int bracketPosition, int length, char[] str) {
        int c = 1, i = 0;
        for (i = bracketPosition; i < length; i++){
            if (str[i] == '('){
                c++;
            }
            if (str[i] == ')'){
                c--;
            }
            if (c == 0){
                break;
            }
        }
        return i;
    }

    public static int findClosingBracketToLeft(int bracketPosition, char[] str) {
        int c = 1, i = 0;
        for (i = bracketPosition; i >= 0; i--){
            if (str[i] == ')'){
                c++;
            }
            if (str[i] == '('){
                c--;
            }
            if (c == 0){
                break;
            }
        }
        return i;
    }

    public static String deleteBrackets(String str) {
        if ((str.charAt(0) == '(') && (str.charAt(str.length()-1) == ')')){
            String tmpStr = str.substring(1, str.length()-1);
            if (checkBrackets(tmpStr)){
                return deleteBrackets(tmpStr);
            }
        }
        return str;
    }
}