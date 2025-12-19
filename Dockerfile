# Build stage
FROM ubuntu:22.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    autoconf \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the source code
COPY . .

# Configure and build
# We touch src/.accepted to bypass the interactive license agreement during build
RUN ./configure && \
    touch src/.accepted && \
    make -C src all

# Final stage
FROM ubuntu:22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libc6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy binaries from the build stage
COPY --from=builder /app/bin ./bin
# Copy library files (world data, player files, etc.) and logs
COPY --from=builder /app/lib ./lib
COPY --from=builder /app/log ./log

# The MUD expects to find the 'lib' directory in its current working directory.
# We'll run it from /app.

# Expose the port requested by the user
EXPOSE 42067

# Run the MUD
# -q: Quick boot (skips rent check, faster startup)
# 42067: The port to listen on
CMD ["./bin/circle", "-q", "42067"]

