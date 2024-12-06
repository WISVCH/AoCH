# AoCH Leaderboard

This project shows the current statistics and leaderboard of CH members for the AoC.

## Guidelines

This script follows the guidelines stated by [Advent of Code](https://www.reddit.com/r/adventofcode/wiki/faqs/automation), namely:

- it includes the emails of the maintainers and a link to the current repo in the User-Agent header for all outbound requests;
- it throttles the requests made to the website by only requesting (private) leaderboard updates every 15 minutes;
- the puzzle for each day is requested only once and 'cached' runtime only, so restarting the server removes the 'cache'.

## Start server

### ENV variables

The following environment variables are expected:

* session
  This is the session cookie of a advent of code user that is enrolled in the leaderboard.
* leaderboard_id
  The id of the AOC leaderboard to show. Default to the CH leaderboard.
* SECRET_KEY_BASE
  A keybase used for security purposes. It can be generated with mix phx.gen.secret. If you dont have mix installed, any other 32 byte long string will do.

### With Mix

To start your dev Phoenix server:

* Run `mix setup` to install and setup dependencies
* Start Phoenix endpoint with `mix phx.server` or inside IEx with `iex -S mix phx.server`

Now you can visit [`localhost:8080`](http://localhost:4000) from your browser.

### With Docker

The project can also be run using the provided `Dockerfile` for this, simply build the docker image, `docker build -t aoch .` and run it: `docker run aoch`

## Questions and contributions

This project is created using the phoenix framework in elixir. I understand these are not the most well-known framework and language. So if you have any questions you can always contact Kasper at [kasperv@ch.tudelft.nl](mailto:kasperv@ch.tudelft.nl).

If you have a feature request and don't know how to do it yourself, please create an issue and send an email to the above email address to let me know about it. I will try to maintain the leaderboard as long as possible!
