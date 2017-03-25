package com.roman_fedorov.csc;

import java.util.Scanner;

/**
 * Created by Roman Fedorov on 22.03.2017.
 */
public class ThirdTask {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Treap<Integer> treap = new Treap<>();
        int commandsCount = scanner.nextInt();
        scanner.nextLine();
        for (int i = 0; i < commandsCount; i++) {
            String[] commands = scanner.nextLine().split(" ");
            int command = Integer.parseInt(commands[0]);
            int argument = Integer.parseInt(commands[1]);
            switch (command) {
                case -1:
                    treap.delete(argument);
                    break;
                case 0:
                    System.out.println(treap.kthMaximum(argument));
                    break;
                case 1:
                    treap.insert(argument);
                    break;
            }
        }
    }
}
