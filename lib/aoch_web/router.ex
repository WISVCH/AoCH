defmodule AoCHWeb.Router do
  use AoCHWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_live_flash
    plug :put_root_layout, html: {AoCHWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", AoCHWeb do
    pipe_through :browser

    get "/", PageController, :today
    get "/:year/day/:day/", PageController, :challenge
    get "/:year/day/:day/challenge", PageController, :challenge
    get "/challenge", PageController, :challenge
    get "/:year/day/:day/challenge", PageController, :challenge
    get "/leaderboard", PageController, :total
    get "/:year/leaderboard", PageController, :total
    get "/leaderboard/today", PageController, :today
    get "/:year/day/:day/leaderboard/today", PageController, :today
    get "/data", APIController, :index
    get "/:year/day/:day/data", APIController, :index
  end

  # Other scopes may use custom stacks.
  # scope "/api", AoCHWeb do
  #   pipe_through :api
  # end

  # Enable LiveDashboard and Swoosh mailbox preview in development
  if Application.compile_env(:aoch, :dev_routes) do
    # If you want to use the LiveDashboard in production, you should put
    # it behind authentication and allow only admins to access it.
    # If your application does not have an admins-only section yet,
    # you can use Plug.BasicAuth to set up some basic authentication
    # as long as you are also using SSL (which you should anyway).
    import Phoenix.LiveDashboard.Router

    scope "/dev" do
      pipe_through :browser

      live_dashboard "/dashboard", metrics: AoCHWeb.Telemetry
    end
  end
end
