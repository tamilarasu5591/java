/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
import java.util.HashSet;
class solution{
    public boolean isvalid(char[][] board){
        HashSet<String> seen = new HashSet<>();
        for(int i=0;i<9;i++){
            for(int j=0;j<9;j++){
                char num = board[i][j];
                if(num != '.'){
                    if(!seen.add(num+ "row" +i)||
                        !seen.add(num+ "col" +j)||
                        !seen.add(num + "box" +i/3 +j/3)){
                            return false;
                        }
                }
            }
        }
        return true;
    }
}