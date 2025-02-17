FROM mcr.microsoft.com/dotnet/sdk:7.0

WORKDIR /app

RUN dotnet tool install --global dbup-cli

COPY ./dbup.yml ./
COPY ./scripts ./scripts


ENV PATH="${PATH}:/root/.dotnet/tools"
ENV CONNSTR="Host=postgres;Port=5432;Database=caruna;Username=caruna;Password=test"

CMD [ "dbup", "upgrade", "-v", "detail" ]