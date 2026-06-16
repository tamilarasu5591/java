/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
class Main {
     Node head;
    class Node {
        int data;
        Node next;
        Node prev;
        Node(int data) {
            this.data = data;
            this.next = null;
            this.prev = null;
        }
    }
    public void insertAtEnd(int data) {
        Node temp = new Node(data);
        if (head == null) {
            head = temp;
            return;
        }
        Node last = head;
        while (last.next != null) {
            last = last.next;
        }
        last.next = temp;
        temp.prev = last;
    }
}