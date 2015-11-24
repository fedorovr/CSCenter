package ru.compscicenter.java2014.collections;

import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map.Entry;
import java.util.List;
import java.util.LinkedList;
import java.util.NoSuchElementException;

/**
 * Created by Roman Fedorov on 01.11.2014.
 */

public class MultiSetImplementation<E> implements MultiSet<E> {

    private HashMap<E, Integer> multiset;

    private int size = 0;

    private void updateSize(final int up) {
        this.size += up;
    }

    public MultiSetImplementation() {
        this.multiset = new HashMap<E, Integer>();
    }

    public MultiSetImplementation(final Collection<? extends E> collection) {
        this.multiset = new HashMap<E, Integer>();
        for (Object collectionElement : collection) {
            if (this.multiset.containsKey(collectionElement)) {
                int backup = this.multiset.get(collectionElement);
                this.multiset.remove(collectionElement);
                this.multiset.put((E) collectionElement, backup + 1);
            } else {
                this.multiset.put((E) collectionElement, 1);
            }
            updateSize(1);
        }
    }

    @Override
    public final int size() {
        return this.size;
    }


    public class MultiSetIterator<E> implements Iterator<E> {
        private E[] elements;
        private int currentObj;
        private int lastRemovedElement;

        MultiSetIterator() {
            elements = (E[]) MultiSetImplementation.this.toArray();
            lastRemovedElement = -1;
            currentObj = -1;
        }

        @Override
        public final E next() {
            if (this.hasNext()) {
                ++currentObj;
                return elements[currentObj];
            } else {
                throw new NoSuchElementException();
            }

        }

        @Override
        public final boolean hasNext() {
            return (currentObj < elements.length - 1);
        }

        @Override
        public final void remove() {
            if (lastRemovedElement == currentObj) {
                throw new IllegalStateException();
            }
            try {
                lastRemovedElement = currentObj;
                MultiSetImplementation.this.remove(elements[currentObj]);
            } catch (Exception e) {
                throw new IllegalStateException();
            }
        }
    }

    @Override
    public final Iterator<E> iterator() {
        return new MultiSetIterator<E>();
    }

    @Override
    public final boolean add(final E e) {
        if (this.multiset.containsKey(e)) {
            int backup = this.multiset.get(e);
            this.multiset.remove(e);
            this.multiset.put(e, backup + 1);
        } else {
            this.multiset.put(e, 1);
        }
        updateSize(1);
        return true;
    }

    public final int add(final E e, final int occurrences) {
        if (occurrences < 0) {
            throw new IllegalArgumentException("Add occurrences count is negative");
        }
        if (this.multiset.containsKey(e)) {
            int backup = this.multiset.get(e);
            this.multiset.remove(e);
            this.multiset.put(e, backup + occurrences);
            updateSize(occurrences);
            return backup;
        } else {
            this.multiset.put(e, occurrences);
            updateSize(occurrences);
            return 0;
        }
    }

    @Override
    public final boolean remove(final Object e) {
        if (this.multiset.containsKey(e)) {
            int backup = this.multiset.get(e);
            this.multiset.remove(e);
            if ((backup - 1) > 0) {
                this.multiset.put((E) e, backup - 1);
            }
            updateSize(-1);
            return true;
        } else {
            return false;
        }
    }

    public final int remove(final Object e, final int occurrences) {
        if (occurrences < 0) {
            throw new IllegalArgumentException("Remove occurrences count is negative");
        }
        if (this.multiset.containsKey(e)) {
            int backup = this.multiset.get(e);
            this.multiset.remove(e);
            if ((backup - occurrences) > 0) {
                this.multiset.put((E) e, backup - occurrences);
            }
            if ((backup - occurrences) >= 0) {
                updateSize(-1 * occurrences);
            } else {
                updateSize(-1 * backup);
            }
            return backup;
        } else {
            return 0;
        }
    }

    public final int count(final Object e) {
        if (this.multiset.containsKey(e)) {
            return this.multiset.get(e);
        } else {
            return 0;
        }
    }

    @Override
    public final boolean containsAll(final Collection<?> c) {
        for (Object collectionElement : c) {
            if (!this.multiset.containsKey(collectionElement)) {
                return false;
            }
        }
        return true;
    }

    @Override
    public final Object[] toArray() {
        List<E> elementList = new LinkedList<E>();
        for (Entry<E, Integer> entry : this.multiset.entrySet()) {
            int countOfElement = entry.getValue();
            E element = entry.getKey();
            for (int q = 0; q < countOfElement; q++) {
                elementList.add(element);
            }
        }
        return elementList.toArray();
    }

    @Override
    public final <T> T[] toArray(final T[] a) {
        if (a == null) {
            throw new NullPointerException("Array in toArray(T[a] a) are null");
        }
        T[] r;
        if (a.length >= size()) {
            r = a;
        } else {
            r = (T[]) java.lang.reflect.Array.newInstance(a.getClass().getComponentType(), size());
        }
        int j = 0;
        for (E c: multiset.keySet()) {
            for (int i = 0; i < multiset.get(c); i++) {
                r[j++] = (T) c;
            }
        }
        return r;
    }

    @Override
    public final boolean removeAll(final Collection<?> c) {
        boolean isAtLeastOneElementRemoved = false;
        for (Object collectionElement : c) {
            if (this.multiset.containsKey(collectionElement)) {
                updateSize(-1 * this.multiset.get(collectionElement));
                this.multiset.remove(collectionElement);
                isAtLeastOneElementRemoved = true;
            }
        }
        return isAtLeastOneElementRemoved;
    }

    @Override
    public final boolean retainAll(final Collection<?> c) {
        int initialSize = size();
        LinkedList tmpList = new LinkedList<E>();
        for (Object elem : c) {
            if (this.multiset.containsKey(elem)) {
                int count = this.multiset.get(elem);
                this.multiset.remove(elem);
                updateSize(-1 * count);
                for (int i = 0; i < count; i++) {
                    tmpList.add(elem);
                }
            }
        }
        int afterExecutingSize = size();
        this.multiset.clear();
        updateSize(-1 * afterExecutingSize);
        if (afterExecutingSize != initialSize) {
            Iterator<? extends E> listIterator = tmpList.iterator();
            while (listIterator.hasNext()) {
                E elem = listIterator.next();
                if (this.multiset.containsKey(elem)) {
                    int backup = this.multiset.get(elem);
                    this.multiset.remove(elem);
                    this.multiset.put(elem, backup + 1);
                } else {
                    this.multiset.put(elem, 1);
                }
                updateSize(1);
            }
        }
        return (initialSize != size());
    }

    @Override
    public final void clear() {
        int backupSize = size();
        this.multiset.clear();
        updateSize(-1 * backupSize);
    }

    @Override
    public final boolean equals(final Object o) {
        try {
            return this.multiset.equals(((MultiSetImplementation) o).multiset);
        } catch (Exception e) {
            return false;
        }
    }

    @Override
    public final int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + this.multiset.hashCode();
        result = prime * result + this.size;
        return result;
    }

    public final boolean contains(final Object o) {
        return this.multiset.containsKey((E) o);
    }

    public final boolean isEmpty() {
        return this.multiset.isEmpty();
    }

    public final boolean addAll(final Collection<? extends E> collection) {
        boolean isAtLeastOneElementAdded = false;
        Iterator<? extends E> e = collection.iterator();
        while (e.hasNext()) {
            E elem = e.next();
            if (this.multiset.containsKey(elem)) {
                int backup = this.multiset.get(elem);
                this.multiset.remove(elem);
                this.multiset.put(elem, backup + 1);
                isAtLeastOneElementAdded = true;
            } else {
                this.multiset.put(elem, 1);
                isAtLeastOneElementAdded = true;
            }
            updateSize(1);
        }
        return isAtLeastOneElementAdded;
    }
}
