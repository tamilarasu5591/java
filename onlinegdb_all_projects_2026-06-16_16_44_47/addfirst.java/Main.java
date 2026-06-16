import java.util.*;
class main{
    public static void main(String[] args){
        ArrayList<Integer> List = new ArrayList<>();
        List.add(10);
        List.add(20);
        List.set(1,30);
        List.addFirst(6);
        List.addLast(55);
        for(Integer name: List){
            System.out.println(name);
        }
    }
}
