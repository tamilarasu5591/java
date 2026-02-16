class left{
    public static void main(String[] args) {
        int arr[][] = {{1,2,3},{4,5,6},{7,8,9}};
        for (int r = 0; r < arr.length; r++) {
            int[] row = arr[r];
            int n = row.length;
            int k = r;
            int[] temp = new int[k];
            for (int i = 0; i < k; i++) {
                temp[i] = row[i];
            }
            for (int i = k; i < n; i++) {
                row[i - k] = row[i];
            }
            for (int i = 0; i < k; i++) {
                row[n - k + i] = temp[i];
            }
        }
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr[i].length; j++) {
                System.out.print(arr[i][j] + " ");
            }
            System.out.println();
        }
    }
}
