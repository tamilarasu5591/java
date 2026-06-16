/******************************************************************************

Welcome to GDB Online.
  GDB online is an online compiler and debugger tool for C, C++, Python, PHP, Ruby, 
  C#, OCaml, VB, Perl, Swift, Prolog, Javascript, Pascal, COBOL, HTML, CSS, JS
  Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
class node {
    int data;
    node next;

    node(int data) {
        this.data = data;
        this.next = null;
    }
}
class LinkedList{
    node head;
    public void add(int data){
        node newNode= new node(data);
            if(head==null){
                head=newNode;
            }
            else{
                node temp=head;
                while(temp.next!=null){
                    temp=temp.next;
                }
                temp.next=newNode;
            }
    }
    public void printList(){
        node temp=head;
        while(temp!=null){
            System.out.println(temp.data+"->");
            temp=temp.next;
        }
        System.out.println("null");
    }
    public static void main(String[] args){
        LinkedList List= new LinkedList();
        List.add(1);
        List.add(2);
        List.printList();
    }
}