class Main {
    static int[] queue = new int[5];
    static int rear = -1;            
    static void enqueue(int value) {
        if (rear == 4) {
            System.out.println("Queue is Full");
            return;
        }
        rear++;             
        queue[rear] = value;    
    }
    public static void main(String[] args) {
        enqueue(10);
        enqueue(20);
        enqueue(30);
        System.out.println("Queue elements:");
        for (int i = 0; i <= rear; i++) {
            System.out.print(queue[i] + " ");
        }
    }
}