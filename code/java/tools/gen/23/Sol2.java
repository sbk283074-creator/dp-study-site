import java.util.ArrayList;
import java.util.List;

public class Sol2 {
    static final int OK = 0;
    static final int NOT_FOUND = 5;

    static int delete(List<Integer> ids, int id) {
        if (ids.remove(Integer.valueOf(id))) {
            return OK;
        }
        return NOT_FOUND;
    }

    public static void main(String[] args) {
        List<Integer> ids = new ArrayList<>(List.of(1, 2, 3));
        int[] attempts = {2, 2, 1, 3, 3};

        for (int id : attempts) {
            int code = delete(ids, id);
            System.out.printf("delete #%d -> exit %d, %d left %s%n",
                    id, code, ids.size(), ids);
        }

        System.out.println();
        System.out.println("the second attempt on the same id is not a failure of the vault");
    }
}
