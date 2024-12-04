defmodule AoCHWeb.PageController do
  use AoCHWeb, :controller

  def today(conn, params) do
    today = AoCH.get_leaderboard_today()
    render(conn, :today, today: today, auto_scroll: params["auto_scroll"] == "true")
  end

  def total(conn, params) do
    total = AoCH.get_leaderboard_year()
    render(conn, :total, scores: total, auto_scroll: params["auto_scroll"] == "true")
  end

  def challenge(conn, params) do
    now = AoCH.now()
    day = if now.month < 12, do: 25, else: now.day
    year = if now.month == 12, do: now.year, else: now.year - 1
    assignment = AoCH.get_challenge(day, year)

    render(conn, :assignment,
      assignment: assignment,
      auto_scroll: params["auto_scroll"] == "true"
    )
  end
end
