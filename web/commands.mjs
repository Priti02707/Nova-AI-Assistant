export function interpret(input, now = new Date()) {
  const command = input.trim().replace(/[?!]+$/, "");
  if (/^(?:(?:what(?: is|'s) (?:the )?)?(?:current )?time|what time is it)$/i.test(command)) {
    return { text: `The time is ${new Intl.DateTimeFormat(undefined, { timeStyle: "short" }).format(now)}.` };
  }
  if (/^(what(?: is|'s) (?:the )?)?(today's |current )?date(?: today)?$/i.test(command)) {
    return { text: `Today is ${new Intl.DateTimeFormat(undefined, { dateStyle: "full" }).format(now)}.` };
  }
  if (/^(tell me )?(a )?joke$/i.test(command)) {
    return { text: "Why did the developer go broke? Because they used up all their cache." };
  }
  if (/^(exit|goodbye|stop)$/i.test(command)) {
    return { text: "Goodbye! You can run another command whenever you like." };
  }
  const site = command.match(/^open (google|youtube)$/i)?.[1].toLowerCase();
  if (site === "google") return { text: "Google is ready to open.", url: "https://www.google.com/", label: "Open Google" };
  if (site === "youtube") return { text: "YouTube is ready to open.", url: "https://www.youtube.com/", label: "Open YouTube" };

  const video = command.match(/^(?:play|search youtube for)\s+(.+)$/i)?.[1];
  if (video) {
    const url = new URL("https://www.youtube.com/results");
    url.searchParams.set("search_query", video);
    return { text: `YouTube search for “${video}”`, url: url.href, label: "View YouTube results" };
  }

  const topic = command.match(/^(?:search wikipedia for|wikipedia)\s+(.+)$/i)?.[1];
  if (topic) {
    const url = new URL("https://en.wikipedia.org/w/index.php");
    url.searchParams.set("search", topic);
    return { text: `Wikipedia search for “${topic}”`, url: url.href, label: "View Wikipedia results" };
  }
  const search = command.match(/^search(?: the web)? for\s+(.+)$/i)?.[1];
  if (search) {
    const url = new URL("https://www.google.com/search");
    url.searchParams.set("q", search);
    return { text: `Web search for “${search}”`, url: url.href, label: "View Google results" };
  }
  if (/^(?:show (?:my )?)?system info$/i.test(command)) {
    return { text: `Browser language: ${navigator.language} · Time zone: ${Intl.DateTimeFormat().resolvedOptions().timeZone}` };
  }
  return null;
}
