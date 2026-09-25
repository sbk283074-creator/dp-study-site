public class Isolation {
    static int sharedCalls;

    static class Shared {
        boolean check() {
            sharedCalls++;
            return sharedCalls == 1;
        }
    }

    static class Fresh {
        private int calls;

        boolean check() {
            calls++;
            return calls == 1;
        }
    }

    public static void main(String[] args) {
        Shared shared = new Shared();
        System.out.println("shared first  = " + shared.check());
        System.out.println("shared second = " + shared.check());

        System.out.println("fresh first   = " + new Fresh().check());
        System.out.println("fresh second  = " + new Fresh().check());
        System.out.println("total shared  = " + sharedCalls);
    }
}
