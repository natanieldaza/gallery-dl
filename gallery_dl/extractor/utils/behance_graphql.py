# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


GetProfileProjects = """\
query GetProfileProjects($username: String, $after: String) {
  user(username: $username) {
    profileProjects(first: 12, after: $after) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        __typename
        adminFlags {
          mature_lock
          privacy_lock
          dmca_lock
          flagged_lock
          privacy_violation_lock
          trademark_lock
          spam_lock
          eu_ip_lock
        }
        canBeBoosted
        colors {
          r
          g
          b
        }
        covers {
          size_202 {
            url
          }
          size_404 {
            url
          }
          size_808 {
            url
          }
        }
        features {
          url
          name
          featuredOn
          ribbon {
            image
            image2x
            image3x
          }
        }
        fields {
          id
          label
          slug
          url
        }
        hasMatureContent
        id
        oid
        isBoosted
        isFeatured
        isHiddenFromWorkTab
        isMatureReviewSubmitted
        isMonaReported
        isOwner
        isFounder
        isPinnedToSubscriptionOverview
        isPrivate
        sourceFiles {
          ...sourceFileWithCoverFields
        }
        matureAccess
        modifiedOn
        name
        owners {
          ...OwnerFields
          images {
            size_50 {
              url
            }
          }
        }
        premium
        publishedOn
        privacyLevel
        profileSectionId
        stats {
          appreciations {
            all
          }
          views {
            all
          }
          comments {
            all
          }
        }
        slug
        tools {
          id
          title
          category
          categoryLabel
          categoryId
          approved
          url
          backgroundColor
        }
        url
      }
    }
  }
}


fragment sourceFileWithCoverFields on SourceFile {
  __typename
  sourceFileId
  projectId
  userId
  creator {
    username
  }
  title
  assetId
  renditionUrl
  mimeType
  size
  category
  licenseType
  unitAmount
  currency
  tier
  hidden
  extension
  hasUserPurchased
  description
  cover {
    coverUrl
    coverX
    coverY
    coverScale
    width
    height
  }
}


fragment OwnerFields on User {
  displayName
  hasPremiumAccess
  id
  isFollowing
  isProfileOwner
  location
  locationUrl
  url
  username
  isMessageButtonVisible
  availabilityInfo {
    availabilityTimeline
    isAvailableFullTime
    isAvailableFreelance
    hiringTimeline {
      key
      label
    }
  }
  creatorPro {
    isActive
    initialSubscriptionDate
  }
  recruiterPro {
    isActive
  }
}
"""

GetMoodboardItemsAndRecommendations = """\
query GetMoodboardItemsAndRecommendations(
  $id: Int!
  $firstItem: Int!
  $afterItem: String
  $shouldGetRecommendations: Boolean!
  $shouldGetItems: Boolean!
  $shouldGetMoodboardFields: Boolean!
) {
  viewer @include(if: $shouldGetMoodboardFields) {
    isOptedOutOfRecommendations
    isAdmin
  }
  moodboard(id: $id) {
    ...moodboardFields @include(if: $shouldGetMoodboardFields)

    items(first: $firstItem, after: $afterItem) @include(if: $shouldGetItems) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        ...nodesFields
      }
    }

    recommendedItems(first: 80) @include(if: $shouldGetRecommendations) {
      nodes {
        ...nodesFields
        fetchSource
      }
    }
  }
}

fragment moodboardFields on Moodboard {
  id
  label
  privacy
  followerCount
  isFollowing
  projectCount
  url
  isOwner
  owners {
    ...OwnerFields
    images {
      size_50 {
        url
      }
      size_100 {
        url
      }
      size_115 {
        url
      }
      size_230 {
        url
      }
      size_138 {
        url
      }
      size_276 {
        url
      }
    }
  }
}

fragment projectFields on Project {
  __typename
  id
  isOwner
  publishedOn
  matureAccess
  hasMatureContent
  modifiedOn
  name
  url
  isPrivate
  slug
  license {
    license
    description
    id
    label
    url
    text
    images
  }
  fields {
    label
  }
  colors {
    r
    g
    b
  }
  owners {
    ...OwnerFields
    images {
      size_50 {
        url
      }
      size_100 {
        url
      }
      size_115 {
        url
      }
      size_230 {
        url
      }
      size_138 {
        url
      }
      size_276 {
        url
      }
    }
  }
  covers {
    size_original {
      url
    }
    size_max_808 {
      url
    }
    size_808 {
      url
    }
    size_404 {
      url
    }
    size_202 {
      url
    }
    size_230 {
      url
    }
    size_115 {
      url
    }
  }
  stats {
    views {
      all
    }
    appreciations {
      all
    }
    comments {
      all
    }
  }
}

fragment exifDataValueFields on exifDataValue {
  id
  label
  value
  searchValue
}

fragment nodesFields on MoodboardItem {
  id
  entityType
  width
  height
  flexWidth
  flexHeight
  images {
    size
    url
  }

  entity {
    ... on Project {
      ...projectFields
    }

    ... on ImageModule {
      project {
        ...projectFields
      }

      colors {
        r
        g
        b
      }

      exifData {
        lens {
          ...exifDataValueFields
        }
        software {
          ...exifDataValueFields
        }
        makeAndModel {
          ...exifDataValueFields
        }
        focalLength {
          ...exifDataValueFields
        }
        iso {
          ...exifDataValueFields
        }
        location {
          ...exifDataValueFields
        }
        flash {
          ...exifDataValueFields
        }
        exposureMode {
          ...exifDataValueFields
        }
        shutterSpeed {
          ...exifDataValueFields
        }
        aperture {
          ...exifDataValueFields
        }
      }
    }

    ... on MediaCollectionComponent {
      project {
        ...projectFields
      }
    }
  }
}

fragment OwnerFields on User {
  displayName
  hasPremiumAccess
  id
  isFollowing
  isProfileOwner
  location
  locationUrl
  url
  username
  availabilityInfo {
    availabilityTimeline
    isAvailableFullTime
    isAvailableFreelance
  }
}
"""
