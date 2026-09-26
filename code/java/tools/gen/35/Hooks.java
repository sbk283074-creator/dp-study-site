import java.util.ArrayList;
import java.util.List;

/** Shutdown steps that must run, in reverse order of registration, exactly once. */
public final class Hooks {

    private final List<Runnable> steps = new ArrayList<>();
    private boolean done;

    public void add(Runnable step) {
        steps.add(step);
    }

    public void run() {
        if (done) {
            System.out.println("  already stopped: " + done);
            return;
        }
        done = true;
        for (int i = steps.size() - 1; i >= 0; i--) {
            steps.get(i).run();
        }
    }

    public boolean stopped() {
        return done;
    }
}
