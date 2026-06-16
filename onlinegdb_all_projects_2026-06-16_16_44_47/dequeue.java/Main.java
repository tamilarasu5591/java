class main{
    static int[] queue={10,20,30};
    static int front=0;
    static int rear=2;
    static void dequeue(){
        if(front>rear){
            System.out.println("empty");
            return;
        }
        System.out.println(queue[front]);
        front++;
    }
    public static void main(String[] args){
    for(int i=front;i<=rear;i++){
        System.out.print(queue[i]+" ");
    }
}
}