sealed interface Command permits Command.ListNotes {
    record ListNotes() implements Command {}
}

class Intruder implements Command {}
