package com.roman_fedorov.csc;

import java.util.Scanner;

public class FirstTask {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Treap<Integer> treap = new Treap<>();
        while (scanner.hasNextLine()) {
            String[] commands = scanner.nextLine().split(" ");
            String command = commands[0];
            Integer argument = Integer.parseInt(commands[1]);
            switch (command) {
                case "insert":
                    treap.insert(argument);
                    break;
                case "exists":
                    System.out.println(treap.exists(argument));
                    break;
                case "delete":
                    treap.delete(argument);
                    break;
                case "next":
                    Integer next = treap.next(argument);
                    System.out.println(next == null ? "none" : next);
                    break;
                case "prev":
                    Integer prev = treap.prev(argument);
                    System.out.println(prev == null ? "none" : prev);
                    break;
            }
        }
    }
}
