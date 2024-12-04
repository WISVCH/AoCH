defmodule AoCHWeb.PageController do
  use AoCHWeb, :controller

  def home(conn, _params) do
    today = AoCH.get_leaderboard_today()
    render(conn, :home, today: today)
  end
end
