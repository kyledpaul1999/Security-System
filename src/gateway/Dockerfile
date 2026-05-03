# ---- Base Stage ----
FROM node:16-alpine AS base
WORKDIR /usr/src/app
COPY package*.json ./

# ---- Dependencies Stage ----
FROM base AS dependencies
RUN npm install --production

# ---- Build Stage ----
FROM base AS build
RUN npm install
COPY . .
RUN npm run build

# ---- Production Stage ----
FROM node:16-alpine AS production
WORKDIR /usr/src/app
COPY --from=dependencies /usr/src/app/node_modules ./node_modules
COPY --from=build /usr/src/app/dist ./dist

EXPOSE 3000
CMD [ "node", "dist/index.js" ]
