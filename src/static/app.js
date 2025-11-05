document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        let participantsHtml = '';
        if (details.participants && details.participants.length > 0) {
          participantsHtml = `
            <div class="participants-section">
              <p><strong>Current Participants:</strong></p>
              <ul class="participants-list" data-activity="${name}">
                ${details.participants.map(participant => `
                  <li>
                    <span class="participant-email">${participant}</span>
                    <button class="delete-icon" onclick="unregisterParticipant('${name}', '${participant}')" title="Remove participant">
                      ×
                    </button>
                  </li>
                `).join('')}
              </ul>
            </div>
          `;
        } else {
          participantsHtml = `
            <div class="participants-section">
              <p><strong>Current Participants:</strong> None yet - be the first to join!</p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to unregister a participant
  async function unregisterParticipant(activityName, email) {
    if (!confirm(`Are you sure you want to remove ${email} from ${activityName}?`)) {
      return;
    }

    // Show immediate feedback
    messageDiv.textContent = "Removing participant...";
    messageDiv.className = "info";
    messageDiv.classList.remove("hidden");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        // Update just the specific activity card instead of refreshing everything
        updateActivityCard(activityName);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering participant:", error);
    }
  }

  // Function to update a specific activity card
  async function updateActivityCard(activityName) {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      
      if (activities[activityName]) {
        const details = activities[activityName];
        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        let participantsHtml = '';
        if (details.participants && details.participants.length > 0) {
          participantsHtml = `
            <div class="participants-section">
              <p><strong>Current Participants:</strong></p>
              <ul class="participants-list" data-activity="${activityName}">
                ${details.participants.map(participant => `
                  <li>
                    <span class="participant-email">${participant}</span>
                    <button class="delete-icon" onclick="unregisterParticipant('${activityName}', '${participant}')" title="Remove participant">
                      ×
                    </button>
                  </li>
                `).join('')}
              </ul>
            </div>
          `;
        } else {
          participantsHtml = `
            <div class="participants-section">
              <p><strong>Current Participants:</strong> None yet - be the first to join!</p>
            </div>
          `;
        }

        // Find and update the specific activity card
        const activityCards = document.querySelectorAll('.activity-card');
        activityCards.forEach(card => {
          const cardTitle = card.querySelector('h4').textContent;
          if (cardTitle === activityName) {
            card.innerHTML = `
              <h4>${activityName}</h4>
              <p>${details.description}</p>
              <p><strong>Schedule:</strong> ${details.schedule}</p>
              <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
              ${participantsHtml}
            `;
          }
        });
      }
    } catch (error) {
      console.error("Error updating activity card:", error);
      // Fallback to full refresh if update fails
      fetchActivities();
    }
  }

  // Make functions available globally
  window.unregisterParticipant = unregisterParticipant;
  window.updateActivityCard = updateActivityCard;

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    // Show immediate feedback
    messageDiv.textContent = "Registering...";
    messageDiv.className = "info";
    messageDiv.classList.remove("hidden");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Update just the specific activity card instead of refreshing everything
        updateActivityCard(activity);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
