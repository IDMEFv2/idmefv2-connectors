/*
 * Copyright (C) 2020 Graylog, Inc.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the Server Side Public License, version 1,
 * as published by MongoDB, Inc.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * Server Side Public License for more details.
 *
 * You should have received a copy of the Server Side Public License
 * along with this program. If not, see
 * <http://www.mongodb.com/licensing/server-side-public-license>.
 */
package org.idmefv2;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import jakarta.inject.Inject;
import org.graylog.events.notifications.EventNotification;
import org.graylog.events.notifications.EventNotificationContext;
import org.graylog.events.notifications.EventNotificationException;
import org.graylog.events.notifications.EventNotificationService;
import org.graylog.events.notifications.PermanentEventNotificationException;
import org.graylog2.plugin.MessageSummary;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

public class Idmefv2Alert implements EventNotification {
    public interface Factory extends EventNotification.Factory<Idmefv2Alert> {
        @Override
        Idmefv2Alert create();
    }

    private final EventNotificationService notificationService;
    private final ObjectMapper objectMapper;

    @Inject
    public Idmefv2Alert(EventNotificationService notificationService, ObjectMapper objectMapper) {
        this.notificationService = notificationService;
        this.objectMapper = objectMapper;
    }

    @Override
    public void execute(EventNotificationContext ctx) throws EventNotificationException {
        final Idmefv2AlertNotificationConfig config =
                (Idmefv2AlertNotificationConfig) ctx.notificationConfig();

        final ImmutableList<MessageSummary> backlog = notificationService.getBacklogForEvent(ctx);

        final Idmefv2Message message = buildIdmefv2Message(ctx, config, backlog);

        try {
            sendToHttp(config.url(), message);
        } catch (IOException e) {
            throw new PermanentEventNotificationException("Failed to send IDMEFv2 message to " + config.url(), e);
        }
    }

    private Idmefv2Message buildIdmefv2Message(EventNotificationContext ctx,
                                               Idmefv2AlertNotificationConfig config,
                                               ImmutableList<MessageSummary> backlog) {
        Idmefv2Message message = new Idmefv2Message();
        message.setVersion("2.D.V08-Dev");
        message.setId(UUID.randomUUID().toString());
        message.setCreateTime(Instant.now().toString());

        message.setOrganisationName(config.organizationName());
        message.setOrganisationId(config.organizationId());

        Idmefv2Message.Analyzer analyzer = new Idmefv2Message.Analyzer();
        analyzer.setName("Graylog SIEM");
        analyzer.setModel("Graylog 7.x");
        analyzer.setCategory(List.of("SIEM.SIEM"));
        message.setAnalyzer(analyzer);

        final String eventTitle = ctx.eventDefinition()
                .map(def -> def.title())
                .orElse("Unknown alert");

        message.setDescription(eventTitle);
        message.setStatus("Event");
        message.setPriority("Medium");
        message.setType(List.of("Cyber"));
        message.setCategory(List.of("Access.Unauthorized"));

        message.setStartTime(ctx.event().eventTimestamp().toString());

        StringBuilder note = new StringBuilder();
        note.append("Event Definition: ").append(eventTitle).append("\n");
        ctx.eventDefinition().ifPresent(def -> {
            if (!def.description().isEmpty()) {
                note.append("Description: ").append(def.description()).append("\n");
            }
        });
        note.append("Event: ").append(ctx.event().message()).append("\n");
        note.append("Backlog size: ").append(backlog.size());
        message.setNote(note.toString());

        return message;
    }

    private void sendToHttp(String url, Idmefv2Message message) throws IOException {
        java.net.URL endpoint = java.net.URI.create(url).toURL();
        HttpURLConnection conn = (HttpURLConnection) endpoint.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        byte[] body = objectMapper.writeValueAsBytes(message);
        try (OutputStream os = conn.getOutputStream()) {
            os.write(body);
        }

        int responseCode = conn.getResponseCode();
        if (responseCode < 200 || responseCode >= 300) {
            throw new IOException("HTTP endpoint returned non-2xx status: " + responseCode);
        }
    }
}
