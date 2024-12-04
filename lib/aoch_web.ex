defmodule AoCHWeb do
  @moduledoc """
  The entrypoint for defining your web interface, such
  as controllers, components, channels, and so on.

  This can be used in your application as:

      use AoCHWeb, :controller
      use AoCHWeb, :html

  The definitions below will be executed for every controller,
  component, etc, so keep them short and clean, focused
  on imports, uses and aliases.

  Do NOT define functions inside the quoted expressions
  below. Instead, define additional modules and import
  those modules here.
  """

  def static_paths, do: ~w(assets fonts images favicon.ico robots.txt)

  def router do
    quote do
      use Phoenix.Router, helpers: false

      # Import common connection and controller functions to use in pipelines
      import Plug.Conn
      import Phoenix.Controller
      import Phoenix.LiveView.Router
    end
  end

  def channel do
    quote do
      use Phoenix.Channel
    end
  end

  def controller do
    quote do
      use Phoenix.Controller,
        formats: [:html, :json],
        layouts: [html: AoCHWeb.Layouts]

      import Plug.Conn
      import AoCHWeb.Gettext

      unquote(verified_routes())
    end
  end

  def live_view do
    quote do
      use Phoenix.LiveView,
        layout: {AoCHWeb.Layouts, :app}

      unquote(html_helpers())
    end
  end

  def live_component do
    quote do
      use Phoenix.LiveComponent

      unquote(html_helpers())
    end
  end

  def html do
    quote do
      use Phoenix.Component

      # Import convenience functions from controllers
      import Phoenix.Controller,
        only: [get_csrf_token: 0, view_module: 1, view_template: 1]

      # Include general helpers for rendering HTML
      unquote(html_helpers())
    end
  end

  defp html_helpers do
    quote do
      # HTML escaping functionality
      import Phoenix.HTML
      # Core UI components and translation
      import AoCHWeb.CoreComponents
      import AoCHWeb.Gettext

      # Shortcut for generating JS commands
      alias Phoenix.LiveView.JS

      # Routes generation with the ~p sigil
      unquote(verified_routes())
    end
  end

  def verified_routes do
    quote do
      use Phoenix.VerifiedRoutes,
        endpoint: AoCHWeb.Endpoint,
        router: AoCHWeb.Router,
        statics: AoCHWeb.static_paths()
    end
  end

  def format_time(nil), do: "-"

  def format_time(seconds) when is_integer(seconds) do
    case seconds do
      s when s < 60 ->
        "#{s} sec"

      s when s < 3600 ->
        m = div(s, 60)
        "#{m}m, #{rem(s, 60)}s"

      s when s < 86400 ->
        h = div(s, 3600)
        m = div(rem(s, 3600), 60)
        "#{h}h, #{m}m"

      s ->
        d = div(s, 86400)
        h = div(rem(s, 86400), 3600)
        "#{d}d, #{h}h"
    end
  end

  def name(name) do
    case name do
      nil -> "Anonymous"
      "Thom Breugelmans" -> "Thom Breugelmans 🎁"
      "KasperVaessen" -> "Kasper Vaessen 🎄"
      "larsvantol" -> "Lars van Tol 🎅"
      name -> name
    end
  end

  @doc """
  When used, dispatch to the appropriate controller/live_view/etc.
  """
  defmacro __using__(which) when is_atom(which) do
    apply(__MODULE__, which, [])
  end
end
