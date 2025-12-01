defmodule AoCH do
  @moduledoc """
  AoCH keeps the contexts that define your domain
  and business logic.

  Contexts are also responsible for managing your data, regardless
  if it comes from the database, an external API or others.
  """

  def get_leaderboard_day(day, year) do
    raw_data = get_data(year)

    ConCache.get_or_store(:cache, "leaderboard_day_#{year}_#{day}", fn ->
      parse_leaderboard_day(raw_data, day, year)
    end)
  end

  def get_leaderboard_year(year) do
    raw_data = get_data(year)

    ConCache.get_or_store(:cache, "leaderboard_#{year}", fn ->
      parse_leaderboard_year(raw_data, year)
    end)
  end

  def get_api_data(day, year) do
    raw_data = get_data(year)

    ConCache.get_or_store(:cache, "data_#{year}_#{day}", fn ->
      leaderboard_day = parse_leaderboard_day(raw_data, day, year)
      leaderboard = parse_leaderboard_year(raw_data, year)
      day_challenge = get_challenge(day, year)

      %{
        assignment: day_challenge,
        today: leaderboard_day |> Enum.map(&assign_time_strings/1),
        total: leaderboard
      }
    end)
  end

  def get_challenge(day, year) do
    ConCache.get_or_store(:cache, "challenge_#{year}_#{day}", fn ->
      %ConCache.Item{value: request_day_challenge(day, year), ttl: :infinity}
    end)
  end

  def now() do
    DateTime.utc_now() |> DateTime.shift_zone!("America/New_York")
  end

  def start_of_day(year, day) do
    now = now()

    %DateTime{
      now
      | year: year,
        month: 12,
        day: day,
        hour: 0,
        minute: 0,
        second: 0,
        microsecond: {0, 0}
    }
  end

  defp get_data(year) do
    last_day = if year < 2025, do: 25, else: 12

    ConCache.get_or_store(:cache, "data_#{year}", fn ->
      for day <- 1..last_day do
        ConCache.delete(:cache, "leaderboard_day_#{year}_#{day}")
        ConCache.delete(:cache, "data_#{year}_#{day}")
      end

      ConCache.delete(:cache, "leaderboard_#{year}")

      request_raw_data(year)
    end)
  end

  defp assign_time_strings(map) do
    map =
      if map[:first_star] do
        Map.put(map, :star1, AoCHWeb.format_time(map[:first_star]))
      else
        map
      end

    if map[:second_star] do
      Map.put(map, :star2, "+ " <> AoCHWeb.format_time(map[:second_star]))
    else
      map
    end
  end

  defp parse_leaderboard_day(data, day, year) do
    data_per_member =
      data
      |> Map.get("members", [])
      |> Enum.map(fn {id, data} -> {id, extract_day_data(data, year, day)} end)
      |> Map.new()

    sort_by_first =
      Enum.sort_by(data_per_member, fn {_id, data} -> data[:unix_first_star] end)
      |> Enum.with_index()

    sort_by_second =
      Enum.sort_by(data_per_member, fn {_id, data} -> data[:unix_second_star] end)
      |> Enum.with_index()

    total = length(sort_by_first)

    data_per_member =
      Enum.reduce(sort_by_first, data_per_member, fn {{id, data}, index}, acc ->
        if data[:unix_first_star] do
          Map.update!(acc, id, fn data ->
            Map.update!(data, :score, &(total - index + &1))
          end)
        else
          acc
        end
      end)

    Enum.reduce(sort_by_second, data_per_member, fn {{id, data}, index}, acc ->
      if data[:unix_second_star] do
        Map.update!(acc, id, fn data ->
          Map.update!(data, :score, &(total - index + &1))
        end)
      else
        acc
      end
    end)
    |> Enum.map(fn {_id, data} -> data end)
    |> Enum.reject(&(&1[:score] == 0))
    |> Enum.sort_by(& &1[:score], :desc)
    |> assign_ranks()
  end

  defp parse_leaderboard_year(data, year) do
    data
    |> Map.get("members", [])
    |> Enum.map(fn {_id, data} -> extract_year_data(data, year) end)
    |> Enum.reject(&(&1[:score] == 0))
    |> Enum.sort_by(& &1[:score], :desc)
    |> assign_ranks()
  end

  defp assign_ranks(data) do
    data
    |> Enum.with_index(1)
    |> Enum.reduce([], fn {item, index}, acc ->
      rank =
        case acc do
          [] -> index
          [%{score: prev_score, rank: prev_rank} | _] when prev_score == item.score -> prev_rank
          _ -> index
        end

      [Map.put(item, :rank, rank) | acc]
    end)
    |> Enum.reverse()
  end

  defp extract_year_data(data, year) do
    last_day = if year < 2025, do: 25, else: 12

    stars =
      1..last_day
      |> Enum.map(fn day ->
        case data["completion_day_level"][Integer.to_string(day)] do
          nil -> 0
          %{"2" => _} -> 2
          _ -> 1
        end
      end)

    %{
      name: data["name"],
      stars: stars,
      score: data["local_score"]
    }
  end

  defp extract_day_data(data, year, day) do
    start_of_day = start_of_day(year, day) |> DateTime.to_unix()

    unix_time_first_star =
      data["completion_day_level"][Integer.to_string(day)]["1"]["get_star_ts"]

    unix_time_second_star =
      data["completion_day_level"][Integer.to_string(day)]["2"]["get_star_ts"]

    time_first_star =
      if unix_time_first_star do
        unix_time_first_star - start_of_day
      end

    time_second_star =
      if unix_time_second_star do
        unix_time_second_star - unix_time_first_star
      end

    %{
      name: data["name"],
      first_star: time_first_star,
      second_star: time_second_star,
      unix_first_star: unix_time_first_star,
      unix_second_star: unix_time_second_star,
      score: 0
    }
  end

  defp request_day_challenge(day, year) do
    url = "https://adventofcode.com/#{year}/day/#{day}"

    {:ok, res} =
      Req.get(url,
        headers: [
          {"cookie", "session=#{Application.get_env(:aoch, :aoc_session_cookie)}"},
          {"User-Agent", "https://github.com/WISVCH/AoCH, beheer@ch.tudelft.nl"}
        ]
      )

    {:ok, html} =
      res.body |> Floki.parse_document()

    html |> Floki.find("article.day-desc") |> List.first() |> Floki.raw_html()
  end

  defp request_raw_data(year) do
    url =
      "https://adventofcode.com/#{year}/leaderboard/private/view/#{Application.get_env(:aoch, :leaderboard_id)}.json"

    {:ok, res} =
      Req.get(url,
        headers: [
          {"cookie", "session=#{Application.get_env(:aoch, :aoc_session_cookie)}"},
          {"User-Agent", "https://github.com/WISVCH/AoCH, beheer@ch.tudelft.nl"}
        ]
      )

    res.body
  end
end
