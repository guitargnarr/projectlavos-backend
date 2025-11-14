FROM gcc:13 AS builder

WORKDIR /app

# Copy source
COPY src/ ./src/
COPY CMakeLists.txt ./

# Install CMake
RUN apt-get update && apt-get install -y cmake

# Build
RUN mkdir build && cd build && cmake .. && make

# Runtime image
FROM debian:bullseye-slim

WORKDIR /app

# Copy binary
COPY --from=builder /app/build/text_processor .

EXPOSE 9000

CMD ["./text_processor"]
