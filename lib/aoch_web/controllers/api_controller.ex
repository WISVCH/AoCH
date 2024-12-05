defmodule AoCHWeb.APIController do
  use AoCHWeb, :controller

  def index(conn, params) do
    now = AoCH.now()
    year = to_int(params["year"]) || if now.month == 12, do: now.year, else: now.year - 1
    day = to_int(params["day"]) || if now.month < 12, do: 25, else: now.day

    data = AoCH.get_api_data(day, year)

    json(conn, data)
  end

  defp to_int(nil), do: nil

  defp to_int(num) do
    String.to_integer(num)
  end
end
