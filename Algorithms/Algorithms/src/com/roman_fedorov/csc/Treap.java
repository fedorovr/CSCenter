package com.roman_fedorov.csc;

import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Created by Roman Fedorov on 21.03.2017.
 */
public class Treap<E extends Comparable<E>> {
    private ThreadLocalRandom random = ThreadLocalRandom.current();
    private Set<Integer> usedPriorities = new HashSet<>();
    private TreapNode root;

    public Treap() {
    }

    public Treap(E[] data) {
        if (data == null || data.length == 0) {
            throw new IllegalArgumentException("No data to construct the treap.");
        }
        root = new TreapNode(data[0]);
        for (int i = 1; i < data.length; i++) {
            insert(data[i]);
        }
    }

    /**
     * Inserts key in treap. NOTE: duplicate keys are not supported
     *
     * @param key key to insert
     */
    public void insert(E key) {
        if (!exists(key)) {
            TreapNode nodeToInsert = new TreapNode(key);
            if (root == null) {
                root = nodeToInsert;
            } else {
                Pair<TreapNode> pair = root.split(key);
                if (pair.getFirst() != null) {
                    root = pair.getFirst().mergeWith(nodeToInsert);
                } else {
                    root = nodeToInsert;
                }
                if (pair.getSecond() != null) {
                    root = root.mergeWith(pair.getSecond());
                }
            }
        }
    }

    public boolean exists(E key) {
        if (root == null) {
            return false;
        }
        return root.find(key) != null;
    }

    /**
     * Returns the smallest element in the treap, which is bigger than given element
     *
     * @param key given element, treap may have or may don't have this element
     * @return next element or null if there are no elements which are bigger than given
     */
    public E next(E key) {
        if (root == null) {
            return null;
        }
        TreapNode nextNode = root.nextNode(key);
        return nextNode == null ? null : nextNode.key;
    }

    /**
     * Returns the biggest element in the treap, which is smaller than given element
     *
     * @param key given element, treap may have or may don't have this element
     * @return previous element or null if there are no elements which are smaller than given
     */
    public E prev(E key) {
        if (root == null) {
            return null;
        }
        TreapNode previousNode = root.previousNode(key);
        return previousNode == null ? null : previousNode.key;
    }

    /**
     * Returns n-th element in increasing order
     *
     * @param n position if element (1-based)
     * @return element at n-th position or null if the position doesn't exist
     */
    public E nthElement(int n) {
        if (root == null || n <= 0 || n > root.subtreeSize) {
            return null;
        } else {
            TreapNode runner = root;
            int runnerPosition = n;
            while (true) {
                if (runner.subtreeSize - (runner.right != null ? runner.right.subtreeSize : 0) == runnerPosition) {
                    return runner.key;
                } else if (runner.left != null && runner.left.subtreeSize >= runnerPosition) {
                    runner = runner.left;
                } else {
                    runnerPosition -= runner.left != null ? runner.left.subtreeSize + 1 : 1;
                    runner = runner.right;
                }
            }
        }
    }

    /**
     * Returns k-th maximum of all elements of treap
     *
     * @param k number of maximum (1-based)
     * @return k-th maximum or null if the maximum doesn't exist
     */
    public E kthMaximum(int k) {
        if (root == null || k <= 0 || k > root.subtreeSize) {
            return null;
        } else {
            return nthElement(root.subtreeSize - k + 1);
        }
    }

    public void delete(E key) {
        if (root == null) {
            return;
        }
        TreapNode node = root.find(key);
        if (node != null) {
            usedPriorities.remove(node.priority);
            if (node.left == null) {
                if (node.right != null) {
                    node.right.parent = node.parent;
                }
                node.updateParent(node.right);
            } else if (node.right == null) {    // left is not null
                node.left.parent = node.parent;
                node.updateParent(node.left);
            } else {                            // right and left are not nulls
                TreapNode newNode = node.left.mergeWith(node.right);
                newNode.parent = node.parent;
                node.updateParent(newNode);
            }
        }
    }

    @Override
    public String toString() {
        return root.toString();
    }

    private class TreapNode {
        E key;
        int priority;
        int subtreeSize;
        TreapNode left;
        TreapNode right;
        TreapNode parent;

        TreapNode(E key) {
            this.key = key;
            int priority = random.nextInt();
            while (usedPriorities.contains(priority)) {
                priority = random.nextInt();
            }
            this.priority = priority;
            subtreeSize = 1;
            usedPriorities.add(priority);
        }

        /**
         * Merges current treap with another one
         *
         * @param otherTreap treap to merge, which should have all keys bigger than in current treap
         * @return merged treap
         */
        TreapNode mergeWith(TreapNode otherTreap) {
            if (otherTreap == null) {
                return this;
            }

            if (priority > otherTreap.priority) {
                TreapNode newRight;
                if (right == null) {
                    newRight = otherTreap;
                } else {
                    newRight = right.key.compareTo(otherTreap.key) > 0 ?
                            otherTreap.mergeWith(right) : right.mergeWith(otherTreap);
                }
                right = newRight;
                newRight.parent = this;
                recalculateSize();
                return this;
            } else {
                TreapNode newLeft;
                if (otherTreap.left == null) {
                    newLeft = this;
                } else {
                    newLeft = otherTreap.left.key.compareTo(key) < 0 ?
                            otherTreap.left.mergeWith(this) : this.mergeWith(otherTreap.left);
                }
                otherTreap.left = newLeft;
                newLeft.parent = otherTreap;
                otherTreap.recalculateSize();
                return otherTreap;
            }
        }

        /**
         * Splits the treap by key
         *
         * @param query a key to split
         * @return Pair of treaps in which all elements in first treap are smaller or equal than query,
         * in the second treap all elements are bigger than query
         */
        Pair<TreapNode> split(E query) {
            if (key.compareTo(query) == 0) {
                TreapNode splitRight = right;
                splitRight.parent = null;
                right = null;
                recalculateSize();
                return new Pair<>(this, splitRight);
            }

            if (key.compareTo(query) < 0) {
                if (right != null) {
                    Pair<TreapNode> rightSplit = right.split(query);
                    right = rightSplit.getFirst();
                    recalculateSize();
                    if (rightSplit.getFirst() != null) {
                        rightSplit.getFirst().parent = this;
                    }
                    if (rightSplit.getSecond() != null) {
                        rightSplit.getSecond().parent = null;
                    }
                    return new Pair<>(this, rightSplit.getSecond());
                } else {
                    return new Pair<>(this, null);
                }
            } else {
                if (left != null) {
                    Pair<TreapNode> leftSplit = left.split(query);
                    left = leftSplit.getSecond();
                    recalculateSize();
                    if (leftSplit.getSecond() != null) {
                        leftSplit.getSecond().parent = this;
                    }
                    if (leftSplit.getFirst() != null) {
                        leftSplit.getFirst().parent = null;
                    }
                    return new Pair<>(leftSplit.getFirst(), this);
                } else {
                    return new Pair<>(null, this);
                }
            }
        }

        /**
         * Returns element with given key
         *
         * @param query a key to search
         * @return element for given key or null if the key doesn't exist
         */
        TreapNode find(E query) {
            TreapNode closest = findClosest(query);
            return closest.key.compareTo(query) == 0 ? closest : null;
        }

        private TreapNode previousForNonExistingKey(E query) {
            TreapNode closest = findClosest(query);
            return closest.key.compareTo(query) > 0 ? root.previousNode(closest.key) : closest;
        }

        private TreapNode nextForNonExistingKey(E query) {
            TreapNode closest = findClosest(query);
            return closest.key.compareTo(query) > 0 ? closest : root.nextNode(closest.key);
        }

        TreapNode previousNode(E query) {
            TreapNode keyInTree = find(query);
            if (keyInTree != null) {
                if (keyInTree.left != null) {
                    TreapNode runner = keyInTree.left;
                    while (runner.right != null) {
                        runner = runner.right;
                    }
                    return runner;
                } else {
                    TreapNode sonOfRunner = keyInTree;
                    TreapNode runner = keyInTree.parent;
                    while (runner != null && runner.right != sonOfRunner) {
                        sonOfRunner = runner;
                        runner = runner.parent;
                    }
                    return runner;
                }
            } else {
                return previousForNonExistingKey(query);
            }
        }

        TreapNode nextNode(E query) {
            TreapNode keyInTree = find(query);
            if (keyInTree != null) {
                if (keyInTree.right != null) {
                    TreapNode runner = keyInTree.right;
                    while (runner.left != null) {
                        runner = runner.left;
                    }
                    return runner;
                } else {
                    TreapNode sonOfRunner = keyInTree;
                    TreapNode runner = keyInTree.parent;
                    while (runner != null && runner.left != sonOfRunner) {
                        sonOfRunner = runner;
                        runner = runner.parent;
                    }
                    return runner;
                }
            } else {
                return nextForNonExistingKey(query);
            }
        }

        void updateParent(TreapNode newAncestor) {
            if (parent == null) {
                root = newAncestor;
                return;
            }
            if (parent.left == this) {
                parent.left = newAncestor;
            } else {
                parent.right = newAncestor;
            }
            TreapNode parentRunner = parent;
            while (parentRunner != null) {
                parentRunner.recalculateSize();
                parentRunner = parentRunner.parent;
            }
        }

        private void recalculateSize() {
            subtreeSize = 1;
            if (left != null) {
                subtreeSize += left.subtreeSize;
            }
            if (right != null) {
                subtreeSize += right.subtreeSize;
            }
        }

        private TreapNode findClosest(E query) {
            if (key.compareTo(query) > 0 && left != null) {
                return left.findClosest(query);
            } else if (key.compareTo(query) < 0 && right != null) {
                return right.findClosest(query);
            } else {
                return this;
            }
        }

        @Override
        public String toString() {
            String debugOutput = "";
            if (left != null) {
                debugOutput += left.toString();
            }
            debugOutput += "TreapNode{key=" + key + ", prio=" + priority + "},";
            if (right != null) {
                debugOutput += right.toString();
            }
            return debugOutput;
        }
    }
}
