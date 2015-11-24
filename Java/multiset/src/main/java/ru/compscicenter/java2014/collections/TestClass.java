package ru.compscicenter.java2014.collections;

import java.util.Arrays;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

/**
 * Created by Roman Fedorov on 01.11.2014.
 */
public final class TestClass {
    private int t;

    private TestClass() {
        this.t = 0;
    }

    public static void main(final String[] args) {
        List<Character> l = new LinkedList<Character>();
        l.add('H'); l.add('E'); l.add('L'); l.add('L'); l.add('O');
        MultiSet ms = new MultiSetImplementation();

        System.out.println(Arrays.toString(ms.toArray()));

        Iterator msIterator = ms.iterator();
        while (msIterator.hasNext()) {
            //System.out.println(msIterator.next());
            if ((Character) msIterator.next() == 'O') {
                msIterator.remove();
            }
        }

        System.out.println(Arrays.toString(ms.toArray()));
        System.out.println(ms.size());
    }
}
