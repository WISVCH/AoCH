defmodule AoCHWeb.PageController do
  use AoCHWeb, :controller

  def today(conn, params) do
    now = AoCH.now()
    year = to_int(params["year"]) || if now.month == 12, do: now.year, else: now.year - 1
    last_day = if year < 2025, do: 25, else: 12

    day =
      to_int(params["day"]) ||
        if now.month < 12 or now.day > last_day, do: last_day, else: now.day

    today = AoCH.get_leaderboard_day(day, year)

    render(conn, :today,
      year: year,
      today: today,
      auto_scroll: params["auto_scroll"] == "true",
      page_title: "Day #{day} leaderboard"
    )
  end

  def total(conn, params) do
    now = AoCH.now()
    year = to_int(params["year"]) || if now.month == 12, do: now.year, else: now.year - 1
    total = AoCH.get_leaderboard_year(year)

    render(conn, :total,
      year: year,
      scores: total,
      auto_scroll: params["auto_scroll"] == "true",
      page_title: "leaderboard"
    )
  end

  def challenge(conn, params) do
    now = AoCH.now()
    year = to_int(params["year"]) || if now.month == 12, do: now.year, else: now.year - 1
    last_day = if year < 2025, do: 25, else: 12

    day =
      to_int(params["day"]) ||
        if now.month < 12 or now.day > last_day, do: last_day, else: now.day

    assignment = AoCH.get_challenge(day, year)

    render(conn, :assignment,
      assignment: assignment,
      year: year,
      auto_scroll: params["auto_scroll"] == "true",
      page_title: "Day #{day} challenge"
    )
  end

  defp to_int(nil), do: nil

  defp to_int(num) do
    String.to_integer(num)
  end
end
