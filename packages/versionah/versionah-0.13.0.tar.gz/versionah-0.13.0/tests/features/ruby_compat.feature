@execute
Feature: Ruby version compatibility
    In order to maintain Ruby version files
    As a user
    We'll want multiple version compatibility

    Scenario Outline: Read version
        Given I have the version <version>
        When I process <file> with <interpreter>
        Then the interpreter returns 0

    Examples:
        | version | file       | interpreter |
        | 1.0.1   | test_wr.rb | ruby18 -c   |
        | 1.0.1   | test_wr.rb | ruby19 -c   |
