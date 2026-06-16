/******************************************************************************

Welcome to GDB Online.
  GDB online is an online compiler and debugger tool for C, C++, Python, PHP, Ruby, 
  C#, OCaml, VB, Perl, Swift, Prolog, Javascript, Pascal, COBOL, HTML, CSS, JS
  Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
class Node {
    int data;
    Node next;

    Node(int data) {
        this.data = data;
        this.next = null;
    }
}

class Stack {
    Node top = null;

    public void push(int data) {
        Node temp = new Node(data);

        if (top == null) {
            top = temp;
        } else {
            temp.next = top;
            top = temp;
        }
    }

    public void pop() {
        if (top == null) {
            System.out.println("Stack is empty");
        } else {
            System.out.println("Popped element = " + top.data);
            top = top.next;
        }
    }

    public void peek() {
        if (top == null) {
            System.out.println("Stack is empty");
        } else {
            System.out.println("Top element = " + top.data);
        }
    }

    public void display() {
        Node temp = top;

        if (top == null) {
            System.out.println("Stack is empty");
        } else {
            while (temp != null) {
                System.out.println(temp.data);
                temp = temp.next;
            }
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Stack s = new Stack();

        s.push(10);
        s.push(20);
        s.push(30);

        System.out.println("Stack elements:");
        s.display();

        s.peek();
        s.pop();

        System.out.println("After pop:");
        s.display();
    }
}