/******************************************************************************

Welcome to GDB Online.
GDB online is an online compiler and debugger tool for C, C++, Python, Java, PHP, Ruby, Perl,
C#, OCaml, VB, Swift, Pascal, Fortran, Haskell, Objective-C, Assembly, HTML, CSS, JS, SQLite, Prolog.
Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
class Stack {
    int arr[];
    int top;
    int size;

    Stack(int size) {
        this.size = size;
        arr = new int[size];
        top = -1;
    }

    public void push(int data) {
        if (top == size - 1) {
            System.out.println("Stack Overflow");
        } else {
            top++;
            arr[top] = data;
        }
    }

    public void pop() {
        if (top == -1) {
            System.out.println("Stack Underflow");
        } else {
            System.out.println("Popped element = " + arr[top]);
            top--;
        }
    }

    public void peek() {
        if (top == -1) {
            System.out.println("Stack is empty");
        } else {
            System.out.println("Top element = " + arr[top]);
        }
    }

    public void display() {
        if (top == -1) {
            System.out.println("Stack is empty");
        } else {
            for (int i = top; i >= 0; i--) {
                System.out.println(arr[i]);
            }
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Stack s = new Stack(5);

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
