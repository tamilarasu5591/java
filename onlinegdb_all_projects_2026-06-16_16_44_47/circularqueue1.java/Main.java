class CircularQueue{
    int[] queue;
    int front;int rear;
    int size;
    int capacity;
    CircularQueue(int capacity){
        this.capacity=capacity;
        queue= new int[capacity];
        front=0;
        rear=-1;
        size=0;
    }
    public void enqueue(int data){
        if(isFull()){
            System.out.println("queue full");
            return;
        }
        rear=(rear+1)%capacity;
        queue[rear]=data;
        size++;
        System.out.println(data);
        
    }
    public int dequeue(){
        if(isEmpty()){
            System.out.println("queue empty");
            return -1;
        }
        return queue[front];
    }
    public boolean isFull(){
        return siuze=capacity;
    }
    public boolean isEmpty(){
        return size==0;
    }
    public void display(){
        if(isEmpty()){
            System.out.println("queue empty");
            return;
        }
        System.out.print("queue:");
        for(int i=0;i<size;i++){
            System.out.print(queue[(front+i)%capacity]+" ");
    }
    System.out.println();
    class Main{
        public static void main(String[] args){
            CircularQueue cq = new CircularQueue(5);
            cq.enqueue(10);
        cq.enqueue(20);
        cq.enqueue(30);
        cq.enqueue(40);
        cq.enqueue(50);

        cq.display();
        System.out.println("Removed: " + cq.dequeue());
        System.out.println("Removed: " + cq.dequeue());

        cq.display();

        cq.enqueue(60);
        cq.enqueue(70);
        cq.display();
        System.out.println("Front Element:" +cq.peek());
        }
    }
    
    